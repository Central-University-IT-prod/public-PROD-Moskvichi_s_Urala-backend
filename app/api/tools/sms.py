from app.config import SMS_ON, SMSAERO_API_KEY, SMSAERO_EMAIL
from datetime import datetime
from . import SmsAero


def send_sms(phone: int, message: str, unixtime: datetime.timestamp = None) -> dict:
    """
    Send sms and return results.

            Parameters:
                    phone (int): Phone number
                    message (str): Message to send
                    unixtime (timestamp): Send a delayed message

            Returns:
                    data (dict): API request result
    """
    print('SMS text:', message)
    if SMS_ON:
        api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
        res = api.send(phone, message, date_send=unixtime)

        print(res.get('data'))

        return res.get('data')
    else:
        print('SMS IS OFF')
