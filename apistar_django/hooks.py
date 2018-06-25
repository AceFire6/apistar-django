import sys

from apistar.http import Response
from django.db import connections, transaction


class DjangoTransactionHook:
    def __init__(self):
        self.atomic = transaction.Atomic(using=None, savepoint=True)

    def on_request(self):
        for conn in connections.all():
            conn.queries_log.clear()
            conn.close_if_unusable_or_obsolete()

        self.atomic.__enter__()

    def on_response(self, response: Response, exc: Exception) -> Response:
        if exc is None:
            self.exit_atomic_block()
        else:
            self.exit_atomic_block_with_error()

        return response

    def on_error(self, response: Response) -> Response:
        self.exit_atomic_block_with_error()
        return response

    def exit_atomic_block_with_error(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.exit_atomic_block(exc_type, exc_value, exc_traceback)

    def exit_atomic_block(self, exc_type=None, exc_value=None, exc_traceback=None):
        self.atomic.__exit__(exc_type, exc_value, exc_traceback)
