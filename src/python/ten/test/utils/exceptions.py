
class TransactionFailed(Exception):
    """Returned when a transaction was mined but the tx_receipt.status is not 1. """
    pass

class TransactionTimeOut(Exception):
    """Returned when a transaction was excepted into the mempool but there was a timeout waiting on the receipt. """
    pass

class TransactionError(Exception):
    """Returned when a transaction was rejected by the mempool. """
    pass