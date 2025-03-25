"""
Servicio para gestionar las notificaciones a los usuarios mediante Telegram
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError

from api.utils.db import get_db_connection
from api.models import UserPreference, InvestmentOpportunity, TelegramConfig

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Servicio para gestionar las notificaciones a los usuarios sobre oportunidades de inversión
    y nuevos listados inmobiliarios en sus zonas de interés.
    """
    
    def __init__(self):
        """Inicializar el servicio de notificaciones"""
        self.db = get_db_connection()
        self.bot = None
        self.telegram_config = self._load_telegram_config()
        self._setup_telegram_bot()
        
    def _load_telegram_config(self) -> TelegramConfig:
        """
        Cargar la configuración de Telegram desde la base de datos o variables de entorno
        
        Returns:
            Configuración de Telegram
        """
        # Intentar cargar desde la base de datos
        config_data = self.db["config"].find_one({"name": "telegram"})
        
        if config_data:
            return TelegramConfig(
                bot_token=config_data.get("bot_token", ""),
                bot_username=config_data.get("bot_username", ""),
                webhook_url=config_data.get("webhook_url"),
                enabled=config_data.get("enabled", False)
            )
        
        # Si no está en la base de datos, intentar cargar desde variables de entorno
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        bot_username = os.environ.get("TELEGRAM_BOT_USERNAME", "")
        
        return TelegramConfig(
            bot_token=bot_token,
            bot_username=bot_username,
            enabled=bool(bot_token and bot_username)
        )
    
    def _setup_telegram_bot(self):
        """Configurar el bot de Telegram si está habilitado"""
        if not self.telegram_config.enabled:
            logger.warning("Telegram bot not enabled. Notifications will not be sent.")
            return
        
        try:
            self.bot = Bot(token=self.telegram_config.bot_token)
            logger.info(f"Telegram bot initialized: {self.telegram_config.bot_username}")
        except TelegramError as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            self.telegram_config.enabled = False
    
    async def send_notification(self, chat_id: str, message: str) -> bool:
        """
        Enviar una notificación a un usuario a través de Telegram
        
        Args:
            chat_id: ID del chat de Telegram
            message: Mensaje a enviar
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.telegram_config.enabled or not self.bot:
            logger.warning("Telegram bot not enabled. Notification not sent.")
            return False
        
        try:
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send notification to {chat_id}: {e}")
            return False
    
    def create_bargain_message(self, opportunity: InvestmentOpportunity) -> str:
        """
        Crear un mensaje para notificar sobre un chollo inmobiliario
        
        Args:
            opportunity: La oportunidad de inversión
            
        Returns:
            Mensaje formateado para enviar por Telegram
        """
        location = f"{opportunity.neighborhood}, {opportunity.city}" if opportunity.neighborhood else opportunity.city
        
        price_diff = ""
        if opportunity.price_difference:
            price_diff = f"<b>{abs(opportunity.price_difference):.1f}% más barato</b> que la media de la zona."
        
        roi = ""
        if opportunity.estimated_roi:
            roi = f"\nRetorno estimado: <b>{opportunity.estimated_roi:.1f}%</b>"
            
        return (
            f"🏠 <b>¡CHOLLO INMOBILIARIO!</b> 🏠\n\n"
            f"<b>{opportunity.title}</b>\n"
            f"📍 {location}\n"
            f"💰 <b>{opportunity.price:,.0f}€</b> ({opportunity.price_per_sqm:,.0f}€/m²)\n"
            f"🔍 {opportunity.size}m² • {opportunity.property_type or 'Propiedad'}\n"
            f"⭐ Puntuación de inversión: <b>{opportunity.investment_score:.1f}/100</b>\n"
            f"{price_diff}{roi}\n\n"
            f"<a href='{opportunity.url}'>Ver propiedad</a>"
        )
    
    async def notify_bargain(self, opportunity: InvestmentOpportunity, user_preference: UserPreference) -> bool:
        """
        Notificar a un usuario sobre un chollo inmobiliario que coincide con sus preferencias
        
        Args:
            opportunity: La oportunidad de inversión
            user_preference: Las preferencias del usuario
            
        Returns:
            True si se notificó correctamente, False en caso contrario
        """
        if not user_preference.telegram_chat_id or not user_preference.notify_bargains:
            return False
            
        # Actualizar la última notificación
        user_preference.last_notification = datetime.now()
        self.db["user_preferences"].update_one(
            {"user_id": user_preference.user_id},
            {"$set": {"last_notification": user_preference.last_notification}}
        )
        
        message = self.create_bargain_message(opportunity)
        return await self.send_notification(user_preference.telegram_chat_id, message)
    
    def save_user_preference(self, preference: UserPreference) -> bool:
        """
        Guardar o actualizar las preferencias de un usuario
        
        Args:
            preference: Preferencias del usuario
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            self.db["user_preferences"].update_one(
                {"user_id": preference.user_id},
                {"$set": {
                    "cities": preference.cities,
                    "neighborhoods": preference.neighborhoods,
                    "min_price": preference.min_price,
                    "max_price": preference.max_price,
                    "min_size": preference.min_size,
                    "min_rooms": preference.min_rooms,
                    "property_types": preference.property_types,
                    "operation_type": preference.operation_type,
                    "min_investment_score": preference.min_investment_score,
                    "bargain_threshold": preference.bargain_threshold,
                    "telegram_chat_id": preference.telegram_chat_id,
                    "notify_bargains": preference.notify_bargains,
                    "notify_new_listings": preference.notify_new_listings,
                    "last_notification": preference.last_notification
                }},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save user preference: {e}")
            return False
    
    def get_user_preference(self, user_id: str) -> Optional[UserPreference]:
        """
        Obtener las preferencias de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Preferencias del usuario o None si no existe
        """
        pref_data = self.db["user_preferences"].find_one({"user_id": user_id})
        if not pref_data:
            return None
            
        return UserPreference(
            user_id=pref_data["user_id"],
            cities=pref_data.get("cities", []),
            neighborhoods=pref_data.get("neighborhoods", []),
            min_price=pref_data.get("min_price"),
            max_price=pref_data.get("max_price"),
            min_size=pref_data.get("min_size"),
            min_rooms=pref_data.get("min_rooms"),
            property_types=pref_data.get("property_types", []),
            operation_type=pref_data.get("operation_type", "sale"),
            min_investment_score=pref_data.get("min_investment_score", 70.0),
            bargain_threshold=pref_data.get("bargain_threshold", 15.0),
            telegram_chat_id=pref_data.get("telegram_chat_id"),
            notify_bargains=pref_data.get("notify_bargains", True),
            notify_new_listings=pref_data.get("notify_new_listings", False),
            last_notification=pref_data.get("last_notification")
        )
    
    def get_matching_user_preferences(self, opportunity: InvestmentOpportunity) -> List[UserPreference]:
        """
        Obtener las preferencias de usuarios que coinciden con una oportunidad
        
        Args:
            opportunity: La oportunidad de inversión
            
        Returns:
            Lista de preferencias de usuarios que coinciden
        """
        matching_preferences = []
        
        # Consultar todas las preferencias de usuarios
        all_preferences = self.db["user_preferences"].find({
            "notify_bargains": True,
            "telegram_chat_id": {"$exists": True, "$ne": None},
            "operation_type": opportunity.operation_type
        })
        
        for pref_data in all_preferences:
            preference = self.get_user_preference(pref_data["user_id"])
            
            # Verificar si la propiedad coincide con las preferencias
            if self._matches_preference(opportunity, preference):
                matching_preferences.append(preference)
                
        return matching_preferences
    
    def _matches_preference(self, opportunity: InvestmentOpportunity, preference: UserPreference) -> bool:
        """
        Verificar si una oportunidad coincide con las preferencias de un usuario
        
        Args:
            opportunity: La oportunidad de inversión
            preference: Las preferencias del usuario
            
        Returns:
            True si coincide, False en caso contrario
        """
        # Verificar ciudad
        if preference.cities and opportunity.city not in preference.cities:
            return False
            
        # Verificar barrio
        if preference.neighborhoods and opportunity.neighborhood and opportunity.neighborhood not in preference.neighborhoods:
            return False
            
        # Verificar precio mínimo
        if preference.min_price is not None and opportunity.price < preference.min_price:
            return False
            
        # Verificar precio máximo
        if preference.max_price is not None and opportunity.price > preference.max_price:
            return False
            
        # Verificar tamaño mínimo
        if preference.min_size is not None and opportunity.size < preference.min_size:
            return False
            
        # Verificar puntuación de inversión mínima
        if opportunity.investment_score < preference.min_investment_score:
            return False
            
        # Verificar tipo de propiedad
        if preference.property_types and opportunity.property_type not in preference.property_types:
            return False
            
        # Verificar si es un chollo según el umbral del usuario
        if not opportunity.is_bargain and opportunity.price_difference is not None:
            if abs(opportunity.price_difference) < preference.bargain_threshold:
                return False
                
        return True
    
    async def notify_matching_users(self, opportunity: InvestmentOpportunity) -> int:
        """
        Notificar a los usuarios cuyas preferencias coinciden con una oportunidad
        
        Args:
            opportunity: La oportunidad de inversión
            
        Returns:
            Número de usuarios notificados
        """
        matching_preferences = self.get_matching_user_preferences(opportunity)
        notify_count = 0
        
        for preference in matching_preferences:
            # Evitar notificaciones demasiado frecuentes al mismo usuario
            if preference.last_notification:
                time_since_last = datetime.now() - preference.last_notification
                if time_since_last < timedelta(hours=4):  # No más de una notificación cada 4 horas
                    continue
            
            success = await self.notify_bargain(opportunity, preference)
            if success:
                notify_count += 1
                
        return notify_count