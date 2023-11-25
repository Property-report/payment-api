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
    # We need to ask for read_write permissions and provide our client ID
    params = {
        'response_type': 'code',
        'scope': 'read_write',
        'client_id':config.CLIENT_ID,
        'redirect_uri':  json_data['return_uri'] + '/users/company/oauth/callback'
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

@payment.route('/create_user', methods=['POST'])
def new_user():
    # Get the response from Stripe
    json_data = request.json
    print(json_data)
    #call method to inset the work item
    results = Sql.new_user(json_data)
    result_dict = []
    for result in results:
        user= result.to_dict()

        result_dict.append(user)
    #build output to return to user
    return jsonify(result_dict)

@payment.route('/update_user/<id>', methods=['PUT'])
def update_user(id):

    json_data = request.json
    #call method to inset the work item
    results = Sql.update_user(id, json_data)
    #build output to return to user
    return build_output(results)

@payment.route('/get_user/<id>', methods=['GET'])
def get_user(id):

    #call method to inset the work item
    results = Sql.get_user({'company_id':id})
    #build output to return to user
    return build_output(results)


@payment.route("/get_stripe_account/<id>", methods=['GET'])
def get_account(id):
    stripe.api_key = config.API_KEY
    return jsonify(stripe.Account.retrieve(id))


@payment.route("/new_payment", methods=['POST'])
def new_payment():
    stripe.api_key = config.API_KEY
    print(request.json)
    if request.json:
        stripe_token = request.json['stripeToken']
        stripe_email = request.json['stripeEmail']
        connected_user_id =  request.json['staff_user_id']
        user_id = request.json['user_id']

        try:
            # Check if there is a Customer already created for this email
            platform_account_customers = stripe.Customer.list()
            platform_customer = [cus for cus in platform_account_customers if cus.email == stripe_email]
            print(platform_customer)
            # If there was no customer, need to create a new platform customer
            staff= Sql.get_user({'company_id' : int(connected_user_id)})

            for user in staff:
                stripe_user = user.stripe_user_id

            clients =  Sql.get_client({'user_id' : int(user_id)})

            if stripe_user:
                if not platform_customer:
                    print("no user")
                    stripe_customer = stripe.Customer.create(
                        email=stripe_email,
                        source=stripe_token,
                    )
                    print(stripe_customer)
                    if not clients:
                        stripe_data={}
                        stripe_data['user_id'] = user_id
                        stripe_data['stripe_user_id'] = stripe_customer.stripe_id
                        stripe_data['email'] = stripe_customer.email
                        stripe_data['account_balance'] = stripe_customer.account_balance
                        stripe_data['creation_time'] = stripe_customer.created
                        stripe_data['currency'] = stripe_customer.currency
                        stripe_data['delinquent'] = stripe_customer.delinquent
                        stripe_data['description'] = stripe_customer.description
                        stripe_data['staff_id'] = request.json['staff_user_id']
                        results = Sql.new_customer_user(stripe_data)
                        print(results)

                    # Need to recreate the token to be able to crete the customer on the connected account too
                    cus_token = stripe.Token.create(
                            customer=stripe_customer.id,
                            stripe_account=stripe_user
                    )
                        # Create the customer in the connected account
                    connected_account_customer = stripe.Customer.create(
                        email=stripe_customer.email,
                        source=cus_token.id,
                        stripe_account=stripe_user,
                    )
                        # Make the charge to the customer on the connected account
                    amount = request.json['amount']
                    try:
                        stripe.Charge.create(
                            amount=amount,
                            currency='gbp',
                            customer=connected_account_customer.id,
                            stripe_account=stripe_user
                        )
                    except stripe.error.CardError as e:
                        return ({"stripe_error": e})
                    except stripe.error.RateLimitError as e:
                        return ({"stripe_error": e})
                    except stripe.error.InvalidRequestError as e:
                        return ({"stripe_error": e})

                    except stripe.error.AuthenticationError as e:
                        # Authentication with Stripe's API failed
                        # (maybe you changed API keys recently)
                        return ({"stripe_error": e})
                    except stripe.error.APIConnectionError as e:
                        # Network communication with Stripe failed
                        return ({"stripe_error": e})
                    except stripe.error.StripeError as e:
                        # Display a very generic error to the user, and maybe send
                        # yourself an email
                        return ({"stripe_error": e})
                    except Exception as e:
                        # Something else happened, completely unrelated to Stripe
                        return ({"stripe_error": e})
                    else:
                        return json.dumps({'stripe_user': stripe_user,'stripe_email' : stripe_email})

                # Just make the charge
                else:
                    # Amount is always in cents
                    if not clients:
                        for cus in platform_customer:
                            stripe_data={}
                            stripe_data['user_id'] = user_id
                            stripe_data['stripe_user_id'] = cus.stripe_id
                            stripe_data['email'] = cus.email
                            stripe_data['account_balance'] = cus.account_balance
                            stripe_data['creation_time'] = cus.created
                            stripe_data['currency'] = cus.currency
                            stripe_data['delinquent'] = cus.delinquent
                            stripe_data['description'] = cus.description
                            stripe_data['staff_id'] = request.json['staff_user_id']
                            results = Sql.new_customer_user(stripe_data)
                            print(results)
                    amount = request.json['amount']
                    print(amount)

                    try:
                        stripe.Charge.create(
                            amount=amount,
                            currency='gbp',
                            source=stripe_token,
                            stripe_account=stripe_user
                        )
                    except stripe.error.CardError as e:
                        return ({"stripe_error": e})
                    except stripe.error.RateLimitError as e:
                        return ({"stripe_error": e})
                    except stripe.error.InvalidRequestError as e:
                        return ({"stripe_error": e})

                    except stripe.error.AuthenticationError as e:
                        # Authentication with Stripe's API failed
                        # (maybe you changed API keys recently)
                        return ({"stripe_error": e})
                    except stripe.error.APIConnectionError as e:
                        # Network communication with Stripe failed
                        return ({"stripe_error": e})
                    except stripe.error.StripeError as e:
                        # Display a very generic error to the user, and maybe send
                        # yourself an email
                        return ({"stripe_error": e})
                    except Exception as e:
                        # Something else happened, completely unrelated to Stripe
                        return ({"stripe_error": e})
                    else:
                        return json.dumps({'stripe_user': stripe_user,'stripe_email' : stripe_email})


def build_output(results):
    result_dict = []
    for key in results:
        output = key.to_dict()
        result_dict.append(output)
    return jsonify(result_dict)
