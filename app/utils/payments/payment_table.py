import os
from model.payments import Payment


TRANSACTION_TYPE_CAMP_PAYMENT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_PAYMENT_ID"))
TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID"))
TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID = int(os.getenv("TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID"))



def get_payment_table(db, payments):
    payment_table = []    
    balance = 0
    for payment in payments:
        balance = balance + payment.payment_amount
        if payment.payment_method == None:
            txn_number = payment.txn_name + ": " + payment.txn_number +" " + "Método de pago: " + "N/A" 
        else:
            txn_number = payment.txn_name + " *" + payment.txn_number+"* " + "Método de pago: " +payment.payment_method  
        payment_table.append(
            {
                "id": payment.id,
                "payment_date": payment.payment_date,
                "txn_number": txn_number, 
                "payment_amount": payment.payment_amount,
                "balance": balance                  
            }
        )
    return payment_table
        
    
def create_payment_table(db, payments):
    
    payment_table = []
    balance = 0
    
    for payment in payments:
        payment_amount = abs(payment.payment_amount)
        
        formated_amount = "{:,.2f}".format(abs(payment.payment_amount))

        
        if payment.payment_method == None:
            txn_number = payment.txn_name + ": " + payment.txn_number +" " + "Método de pago: " + "N/A" 
        else:
            txn_number = payment.txn_name + " *" + payment.txn_number+"* " + "Método de pago: " +payment.payment_method  
    
        
        payment_row = {
                "id": payment.id,
                "payment_date": payment.payment_date,
                "txn_number": txn_number, 
                "charge": "",
                "pay": "",
                "balance": ""             
            }
        
        if payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID):
            payment_row["pay"] = payment.currency_symbol + formated_amount + " " + payment.currency_acronym
            balance = balance - payment_amount
            formated_balance = "{:,.2f}".format(balance)
            payment_row["balance"] = payment.currency_symbol + formated_balance + " " + payment.currency_acronym  
            
        else:
            payment_row["charge"] = payment.currency_symbol + formated_amount + " " + payment.currency_acronym
            balance = balance + payment_amount
            formated_balance = "{:,.2f}".format(balance)
            payment_row["balance"] = payment.currency_symbol + formated_balance + " " + payment.currency_acronym  
            
        payment_table.append(payment_row)
        
    return payment_table    


def create_payment_table_unformatted(db, payments):
    
    payment_table = []
    balance = 0
    
    for payment in payments:
        payment_amount = abs(payment.payment_amount)
        
        formated_amount = "{:.2f}".format(abs(payment.payment_amount))

        
        if payment.payment_method == None:
            txn_number = payment.txn_name + ": " + payment.txn_number +" " + "Método de pago: " + "N/A" 
        else:
            txn_number = payment.txn_name + " *" + payment.txn_number+"* " + "Método de pago: " +payment.payment_method  
    
        
        payment_row = {
                "id": payment.id,
                "payment_date": payment.payment_date,
                "txn_number": txn_number, 
                "charge": "",
                "pay": "",
                "balance": ""             
            }
        
        if payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID):
            payment_row["pay"] = payment.currency_symbol + formated_amount + " " + payment.currency_acronym
            balance = balance - payment_amount
            formated_balance = "{:.2f}".format(balance)
            payment_row["balance"] = formated_balance
            
        else:
            payment_row["charge"] = payment.currency_symbol + formated_amount + " " + payment.currency_acronym
            balance = balance + payment_amount
            formated_balance = "{:.2f}".format(balance)
            print(formated_balance)
            payment_row["balance"] = formated_balance
            
        payment_table.append(payment_row)
        
    return payment_table    


def get_camper_balance_per_camp(db, camper_id, camp_id):
    payments = (
        db.query(Payment)
        .filter(Payment.camper_id == camper_id, Payment.camp_id == camp_id)
        .order_by(Payment.payment_date.asc()).all()
        )
    balance = 0
    for payment in payments:
        payment_amount = abs(payment.payment_amount)
        
        if payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID):
            balance = balance - payment_amount
                   
        else:
            balance = balance + payment_amount

    balance = round(balance, 2)
    
    return balance

def get_camper_total_balance(db, camper_id):
    payments = (
        db.query(Payment)
        .filter(Payment.camper_id == camper_id)
        .order_by(Payment.payment_date.asc()).all()
        )
    balance = 0
    for payment in payments:
        payment_amount = abs(payment.payment_amount)
        
        
        if payment.txn_type_id in (TRANSACTION_TYPE_CAMP_PAYMENT_ID,TRANSACTION_TYPE_CAMP_MANUAL_DISCOUNT_ID,TRANSACTION_TYPE_CAMP_DISCOUNT_UPFRONT_PAYMENT_ID):
            balance = balance - payment_amount
            
                   
        else:
            balance = balance + payment_amount

    balance = round(balance, 2)
        
    return balance