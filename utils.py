import threading
import time
from collections import deque
import functools
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Debouncer:
    """
    Ejecuta una función después de un período de inactividad.
    Cada llamada a `call` reinicia el temporizador.
    """
    def __init__(self, func, wait: float):
        """
        :param func: función a ejecutar tras el período de inactividad
        :param wait: tiempo en segundos de espera tras la última llamada
        """
        self.func = func
        self.wait = wait
        self._timer = None
        self._lock = threading.Lock()

    def call(self, *args, **kwargs):
        """
        Programa la ejecución de `func(*args, **kwargs)` tras `wait` segundos de inactividad.
        """
        with self._lock:
            # Si ya había un temporizador vivo, cancelarlo
            if self._timer and self._timer.is_alive():
                self._timer.cancel()
            # Crear nuevo temporizador
            self._timer = threading.Timer(self.wait, self.func, args=args, kwargs=kwargs)
            self._timer.daemon = True
            self._timer.start()


class RateLimiter:
    """
    Limitador de velocidad tipo "sliding window".
    Permite un máximo de `max_calls` en cada ventana de `period` segundos.
    """
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self._calls = deque()
        self._lock = threading.Lock()

    def allow(self) -> bool:
        """
        Indica si se permite una nueva llamada en la ventana actual.
        :return: True si la llamada está permitida, False si se excede la cuota.
        """
        with self._lock:
            now = time.time()
            # Descartar timestamps fuera de la ventana
            while self._calls and now - self._calls[0] > self.period:
                self._calls.popleft()
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
            return False


def retry_with_backoff(
    max_attempts: int = 5,
    initial_delay: float = 1.0,
    factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para reintentos con back-off exponencial ante excepciones.

    :param max_attempts: número máximo de intentos (incluye el inicial)
    :param initial_delay: retardo antes del primer reintento
    :param factor: factor de crecimiento del retardo
    :param max_delay: retardo máximo entre intentos
    :param exceptions: tupla de excepciones que disparan reintento
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"[{func.__name__}] Falló tras {attempt} intentos: {e}")
                        raise
                    logger.warning(
                        f"[{func.__name__}] Error en intento {attempt}: {e}. Reintentando en {delay}s..."
                    )
                    time.sleep(delay)
                    delay = min(delay * factor, max_delay)
        return wrapper
    return decorator
