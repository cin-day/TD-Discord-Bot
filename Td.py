import requests
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv('TD_KEY')

def makeAccountBalanceRequests (AccID):
    response = requests.get(
        'https://api.td-davinci.com/api/accounts/' + AccID,
        headers = { 'Authorization': KEY },
        json={ 'continuationToken': '' }
    )
    balance = response.json() ['result'] ['bankAccount'] ['balance']
    balance ='{}'.format(balance)
    return balance

# def makeCustomerRequests (custID):
#     response = requests.get(
#         'https://api.td-davinci.com/api/customers/' + custID,
#         headers = { 'Authorization': KEY },
#         json={ 'continuationToken': '' }
#     )
#     return response.json()

def makeTransferReceiptRequests (transferID):
    response = requests.get(
        'https://api.td-davinci.com/api/transfers/' + transferID,
        headers = { 'Authorization': KEY},
        json={ 'continuationToken': '' }
    )
    return response.json()

def makeCustNameRequests (CustID):
    response = requests.get(
        'https://api.td-davinci.com/api/customers/' + CustID,
        headers = { 'Authorization': KEY},
        json={ 'continuationToken': '' }
    )

    customer = response.json()
    if customer ['statusCode'] == 200:
        customerName = customer ['result'] ['givenName'] + ' ' + customer ['result'] ['surname']
        return customerName
    else:
        return str(customer ['statusCode'])

def getCustIDfromAccID (AccID):
    response = requests.get(
        'https://api.td-davinci.com/api/accounts/' + AccID,
        headers = { 'Authorization': KEY},
        json={ 'continuationToken': '' }
    )

    customerId = response.json() ['result']['bankAccount']['relatedCustomerId']
    return customerId

def makeTransfer (amount, sender, recipient, message):
    response = requests.post(
        'https://api.td-davinci.com/api/transfers',
        headers = {'Authorization': KEY},
        json={
            'amount': amount,
            'currency': 'CAD',
            'fromAccountId': sender,
            'receipt': "{ \"Message\": \"" + message + "\"}",
            'toAccountId': recipient
        }
    )
    transac_response=response.json()

    if transac_response ['statusCode'] == 200:
        return transac_response ['result']['id']
    else:
        return False