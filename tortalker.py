import codecs
import requests
import json
import base64
from flask import Flask, request, url_for, make_response, send_file
app = Flask(__name__)

password=""

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

@app.route( "/getinvoice", methods=[ 'POST', 'GET' ] )
@app.route( "/getinvoice/", methods=[ 'POST', 'GET' ] )
def getinvoice():
    from flask import request
    pw = request.args.get( "pw" )
    if str( pw ) == password:
        amt = request.args.get( "amt" )
        memo = request.args.get( "memo" )
        webhook = request.args.get( "webhook" )
        host = request.args.get( "host" )
        endpoint = host
        port_start = host.find( ":", 6 )
        endpoint_has_port = port_start >= 0
        if ( endpoint_has_port ):
            endpoint_without_port = endpoint[ :endpoint.find( ":", 6 ) ]
        else:
            endpoint_without_port = endpoint
        endpoint_is_tor_address = ( endpoint_without_port[ -6: ] == ".onion" )
        apikey = request.args.get( "apikey" )
        url = host + "/api/v1/payments"
        payload = '{"out": false, "amount": ' + amt + ', "memo": "' + memo + '", "webhook": "' + webhook + '"}'
        headers = {
            "X-Api-Key": apikey,
            "Content-type": "application/json"
        }
        if ( endpoint_is_tor_address ):
            query = requests.post( url, data=payload, headers=headers, proxies=proxies )
        else:
            query = requests.post( url, data=payload, headers=headers )
        return query.text
    else:
        return "wrong password"

@app.route( "/checkinvoice", methods=[ 'POST', 'GET' ] )
@app.route( "/checkinvoice/", methods=[ 'POST', 'GET' ] )
def checkinvoice():
    from flask import request
    pw = request.args.get( "pw" )
    if str( pw ) == password:
        pmthash = request.args.get( "pmthash" )
        host = request.args.get( "host" )
        endpoint = host
        port_start = host.find( ":", 6 )
        endpoint_has_port = port_start >= 0
        if ( endpoint_has_port ):
            endpoint_without_port = endpoint[ :endpoint.find( ":", 6 ) ]
        else:
            endpoint_without_port = endpoint
        endpoint_is_tor_address = ( endpoint_without_port[ -6: ] == ".onion" )
        apikey = request.args.get( "apikey" )
        url = host + "/api/v1/payments/" + pmthash
        headers = {
            "X-Api-Key": apikey,
            "Content-type": "application/json"
        }
        if ( endpoint_is_tor_address ):
            query = requests.get( url, headers=headers, proxies=proxies )
        else:
            query = requests.get( url, headers=headers )
        return query.text
    else:
        return "wrong password"

@app.route( "/get-lnd-invoice", methods=[ 'GET', 'POST' ] )
@app.route( "/get-lnd-invoice/", methods=[ 'GET', 'POST' ] )
def get_lnd_invoice():
    pw = request.args.get( "pw" )
    if str( pw ) != password:
        return '{"status":"error","message":"wrong password"}'
    endpoint = request.args.get( "endpoint" )
    port_start = endpoint.find( ":", 6 )
    endpoint_has_port = port_start >= 0
    if ( endpoint_has_port ):
        endpoint_without_port = endpoint[ :endpoint.find( ":", 6 ) ]
    else:
        endpoint_without_port = endpoint
        endpoint = endpoint + ":8080"
    endpoint_is_tor_address = ( endpoint_without_port[ -6: ] == ".onion" )
    url = endpoint + "/v1/invoices"
    macaroon = request.args.get( "macaroon" )
    amount = request.args.get( "amount" )
    memo = request.args.get( "memo" )
    headers = { "Grpc-Metadata-macaroon": macaroon}
    data = {
        "value": amount,
        "memo": memo,
        "private": True,
    }
    if ( endpoint_is_tor_address ):
        r = requests.post( url, headers=headers, data=json.dumps( data ), proxies=proxies, verify=False )
    else:
        r = requests.post( url, headers=headers, data=json.dumps( data ) )
    try:
        resp_content = r.json()
    except ValueError:
        return '{"status":"error","message":"something went wrong connecting to lnd. Try adding an s after the http. Tortalker is not broken so do not blame Super Testnet."}'
    invdata = resp_content
    invoice = invdata[ "payment_request" ]
    pmthash = codecs.encode(base64.b64decode( invdata[ "r_hash" ].encode('utf-8')), 'hex')
    return '{"status":"success","invoice":"' + invoice + '","pmthash":"' + pmthash + '"}'

#call check-lnd-invoice with a command like this one: http://localhost:5000/check-lnd-invoice/?endpoint=http://185.117.75.49:7012&macaroon=0201036c6e640258030a10218e80ed6877232c53110590120b9fc91201301a160a0761646472657373120472656164120577726974651a170a08696e766f69636573120472656164120577726974651a0f0a076f6e636861696e120472656164000006208b515396dcbe8d1c1bff7da919f1c03c60c1f622e

@app.route( "/check-lnd-invoice", methods=[ 'GET', 'POST' ] )
@app.route( "/check-lnd-invoice/", methods=[ 'GET', 'POST' ] )
def check_lnd_invoice():
    pw = request.args.get( "pw" )
    if str( pw ) != password:
        return '{"status":"error","message":"wrong password"}'
    endpoint = request.args.get( "endpoint" )
    port_start = endpoint.find( ":", 6 )
    endpoint_has_port = port_start >= 0
    if ( endpoint_has_port ):
        endpoint_without_port = endpoint[ :endpoint.find( ":", 6 ) ]
    else:
        endpoint_without_port = endpoint
        endpoint = endpoint + ":8080"
    endpoint_is_tor_address = ( endpoint_without_port[ -6: ] == ".onion" )
    pmthash = request.args.get( "pmthash" )
    url = endpoint + "/v1/invoice/" + pmthash
    macaroon = request.args.get( "macaroon" )
    headers = { "Grpc-Metadata-macaroon": macaroon}
    if ( endpoint_is_tor_address ):
        r = requests.get( url, headers=headers, proxies=proxies, verify=False )
    else:
        r = requests.get( url, headers=headers )
    invdata = r.json()
    state = invdata[ "state" ]
    return '{"status":"success","state":"' + state + '"}'

#call get-lnd-hodl-invoice with a command like this one: http://localhost:5000/get-lnd-hodl-invoice/?endpoint=http://185.117.75.49:7012&macaroon=0201036c6e640258030a10218e80ed6877232c53110590120b9fc91201301a160a0761646472657373120472656164120577726974651a170a08696e766f69636573120472656164120577726974651a0f0a076f6e636861696e120472656164000006208b515396dcbe8d1c1bff7da919f1c03c60c$

@app.route( "/get-lnd-hodl-invoice", methods=[ 'GET', 'POST' ] )
@app.route( "/get-lnd-hodl-invoice/", methods=[ 'GET', 'POST' ] )
def get_lnd_hodl_invoice():
    pw = request.args.get( "pw" )
    if str( pw ) != password:
        return '{"status":"error","message":"wrong password"}'
    endpoint = request.args.get( "endpoint" )
    port_start = endpoint.find( ":", 6 )
    endpoint_has_port = port_start >= 0
    if ( endpoint_has_port ):
        endpoint_without_port = endpoint[ :endpoint.find( ":", 6 ) ]
    else:
        endpoint_without_port = endpoint
        endpoint = endpoint + ":8080"
    endpoint_is_tor_address = ( endpoint_without_port[ -6: ] == ".onion" )
    url = endpoint + "/v2/invoices/hodl"
    macaroon = request.args.get( "macaroon" )
    amount = request.args.get( "amount" )
    memo = request.args.get( "memo" )
    pmthash = request.args.get( "pmthash" )
    headers = { "Grpc-Metadata-macaroon": macaroon}
    data = {
        "hash": base64.b64encode( bytes.fromhex( pmthash ) ).decode(),
        "value": amount,
        "memo": memo,
    }
    if ( endpoint_is_tor_address ):
        r = requests.post( url, headers=headers, data=json.dumps( data ), proxies=proxies, verify=False )
    else:
        r = requests.post( url, headers=headers, data=json.dumps( data ) )
    invdata = r.json()
    invoice = invdata[ "payment_request" ]
    return '{"status":"success","invoice":"' + invoice + '"}'

@app.route( "/cancel-lnd-invoice", methods=[ 'GET', 'POST' ] )
@app.route( "/cancel-lnd-invoice/", methods=[ 'GET', 'POST' ] )
def cancel_lnd_invoice():
    pw = request.args.get( "pw" )
    if str( pw ) != password:
        return '{"status":"error","message":"wrong password"}'
    endpoint = request.args.get( "endpoint" )
    port_start = endpoint.find( ":", 6 )
    endpoint_has_port = port_start >= 0
    if ( endpoint_has_port ):
        endpoint_without_port = endpoint[ :endpoint.find( ":", 6 ) ]
    else:
        endpoint_without_port = endpoint
        endpoint = endpoint + ":8080"
    endpoint_is_tor_address = ( endpoint_without_port[ -6: ] == ".onion" )
    url = endpoint + "/v2/invoices/cancel"
    macaroon = request.args.get( "macaroon" )
    pmthash = request.args.get( "pmthash" )
    headers = { "Grpc-Metadata-macaroon": macaroon}
    data = {
        "payment_hash": base64.b64encode( bytes.fromhex( pmthash ) ).decode(),
    }
    if ( endpoint_is_tor_address ):
        r = requests.post( url, headers=headers, data=json.dumps( data ), proxies=proxies, verify=False )
    else:
        r = requests.post( url, headers=headers, data=json.dumps( data ) )
    response = json.dumps( r.json() )
    if ( response == "{}" ):
        return '{"status":"success"}'
    return '{"status":"failure"}'

#call settle-lnd-invoice with a command like this one: http://localhost:5000/settle-lnd-invoice/?endpoint=http://185.117.75.49:7012&macaroon=0201036c6e640258030a10218e80ed6877232c53110590120b9fc91201301a160a0761646472657373120472656164120577726974651a170a08696e766f69636573120472656164120577726974651a0f0a076f6e636861696e120472656164000006208b515396dcbe8d1c1bff7da919f1c03c60c1f62$

@app.route( "/settle-lnd-invoice", methods=[ 'GET', 'POST' ] )
@app.route( "/settle-lnd-invoice/", methods=[ 'GET', 'POST' ] )
def settle_lnd_invoice():
    pw = request.args.get( "pw" )
    if str( pw ) != password:
        return '{"status":"error","message":"wrong password"}'
    endpoint = request.args.get( "endpoint" )
    port_start = endpoint.find( ":", 6 )
    endpoint_has_port = port_start >= 0
    if ( endpoint_has_port ):
        endpoint_without_port = endpoint[ :endpoint.find( ":", 6 ) ]
    else:
        endpoint_without_port = endpoint
        endpoint = endpoint + ":8080"
    endpoint_is_tor_address = ( endpoint_without_port[ -6: ] == ".onion" )
    url = endpoint + "/v2/invoices/settle"
    macaroon = request.args.get( "macaroon" )
    preimage = request.args.get( "preimage" )
    headers = { "Grpc-Metadata-macaroon": macaroon}
    data = {
        "preimage": base64.b64encode( bytes.fromhex( preimage ) ).decode(),
    }
    if ( endpoint_is_tor_address ):
        r = requests.post( url, headers=headers, data=json.dumps( data ), proxies=proxies, verify=False )
    else:
        r = requests.post( url, headers=headers, data=json.dumps( data ) )
    response = json.dumps( r.json() )
    if ( response == "{}" ):
        return '{"status":"success"}'
    return '{"status":"failure"}'

if __name__ == "__main__":
    app.run( port=5001 )
