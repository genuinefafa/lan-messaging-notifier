"""Base notifier class - Interface para todos los notificadores."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseNotifier(ABC):
    """Clase base abstracta para notificadores."""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el notificador.

        Args:
            config: Diccionario con la configuración específica del notificador
        """
        self.config = config
        self.validate_config()

    @abstractmethod
    def validate_config(self) -> None:
        """
        Valida que la configuración tenga todos los campos requeridos.

        Raises:
            ValueError: Si falta alguna configuración requerida
        """
        pass

    @abstractmethod
    def send_message(self, message: str, **kwargs) -> bool:
        """
        Envía un mensaje a través del notificador.

        Args:
            message: El mensaje a enviar
            **kwargs: Argumentos adicionales específicos del notificador

        Returns:
            True si el mensaje se envió exitosamente, False en caso contrario

        Raises:
            Exception: Si hay un error al enviar el mensaje
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Prueba la conexión con el servicio.

        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        pass

    def get_name(self) -> str:
        """
        Retorna el nombre del notificador.

        Returns:
            Nombre del notificador
        """
        return self.__class__.__name__.replace('Notifier', '').lower()
