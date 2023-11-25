from flask import request, Blueprint, jsonify, current_app, redirect, session
import stripe
from payments_api import config
import urllib
import requests
import os
from payments_api.sql import Sql
import json

payment = Blueprint('payments', __name__)


@payment.route('/authorize', methods=['GET'])
def authorize():
    # Build the URI for letting a Stripe user authorize our app to make charges on their behalf
    json_data = request.json

    site = config.SITE + config.AUTHORIZE_URI

    print(json_data['email'])

    # We need to ask for read_write permissions and provide our client ID
    params = {
        'response_type': 'code',
        'scope': 'read_write',
        'client_id':config.CLIENT_ID,
        'redirect_uri':  json_data['return_uri'] + '/users/company/oauth/callback',
        'email':json_data['email'],
        'state':json_data['state']
    }

    # Redirect to Stripe /oauth/authorize endpoint
    return jsonify(site + '?' + urllib.parse.urlencode(params))


@payment.route('/oauth/callback')
def callback():
    # Get the response from Stripe
    code = request.json
    print(code)
    # Build the dict needed to get a token
    data = {
        'client_secret': config.API_KEY,
        'grant_type': 'authorization_code',
        'client_id': config.CLIENT_ID,
        'code': code
    }

    # Make /oauth/token endpoint POST request
    url = config.SITE + config.TOKEN_URI
    resp = requests.post(url, params=data)
    # Show a view to actually make a fake charge on behalf of the connected account
    return jsonify(resp.json())



@payment.route("/get_onetime_payment_session_external", methods=['GET'])
def get_onetime_payment_session_external():
    stripe.api_key = config.API_KEY
    stripe_email = request.json['stripeEmail']
    try:
 
        platform_account_customers = stripe.Customer.list()
        platform_customer = [cus for cus in platform_account_customers if cus.email == stripe_email]

        if not platform_customer:

            stripe_customer = stripe.Customer.create(
                email=stripe_email
            )
        else:
            for cus in platform_customer:
                stripe_customer=cus

        line_items=[]

        oneoff_payment=request.json['oneoff_payment']


        if oneoff_payment != []:
            for x in oneoff_payment:
                amount =x['amount']
                name =x['name']


                line_items.append(
                {
                'price_data': {
                'currency': 'gbp',
                'unit_amount': int(amount),
                'product_data': {
                    'name': name,
                },
                },
                "quantity": 1
                })

            
        if oneoff_payment != []:
            print(request.json['client_reference_id'])
            stripe_session = stripe.checkout.Session.create(
                allow_promotion_codes=True,
                payment_method_types=['card'],
                line_items=line_items,
                customer=stripe_customer.id,
                success_url=request.json['success_url'],
                cancel_url=request.json['cancel_url'],
                client_reference_id=request.json['client_reference_id'],
                mode="payment"
            )
            print(stripe_session)
            print("stripe_session")
            print("****************")


    except stripe.error.CardError as e:
        body = e.json_body
        err  = body.get('error', {})
        return json.dumps({"stripe_error": err.get('message')})
    except stripe.error.RateLimitError as e:
        body = e.json_body
        err  = body.get('error', {})
        return json.dumps({"stripe_error": err.get('message')})
    except stripe.error.InvalidRequestError as e:
        body = e.json_body
        err  = body.get('error', {})
        return json.dumps({"stripe_error": err.get('message')})
    except stripe.error.AuthenticationError as e:
        body = e.json_body
        err  = body.get('error', {})
        return json.dumps({"stripe_error": err.get('message')})
    except stripe.error.APIConnectionError as e:
        body = e.json_body
        err  = body.get('error', {})
        return json.dumps({"stripe_error": err.get('message')})
    except stripe.error.StripeError as e:
        body = e.json_body
        err  = body.get('error', {})
        return json.dumps({"stripe_error": err.get('message')})
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        return json.dumps({"stripe_error": e})
    else:
        return json.dumps({"stripe_session":stripe_session,'stripe_email' : stripe_email})

def build_output(results):
    result_dict = []
    for key in results:
        output = key.to_dict()
        result_dict.append(output)
    return jsonify(result_dict)
