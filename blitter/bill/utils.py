from . import models


def get_bill_status(bill):
    try:
        if bill.settled_amount and bill.settled_amount >= bill.amount:
            return models.Bill.BillStatus.FULFILLED
        return models.Bill.BillStatus.UNSETTLED
    except AttributeError:
        raise AttributeError('settled_amount needs to be annotated.')
