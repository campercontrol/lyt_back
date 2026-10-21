
from fastapi import APIRouter, Depends,Response, BackgroundTasks,UploadFile, Request
from sqlalchemy.orm import Session

from utils.email_tools import (
    send_simple_message,
    send_attachment_message,
    send_html_message,
    send_scheduled_message,
    send_create_template,
    get_template,
    send_message_by_template_id,
    update_template,
    send_get_webhook,
    add_webhook,
    get_domain,
    update_webhook,
    delete_domain
)    
from schema.email import EmailWebhookCreate,WebhookUrl

from datetime import datetime, timedelta
import json
import pytz

newMexZone = pytz.timezone("America/Mexico_City") 

email_routes = APIRouter()
# Endpoints sin autenticacion (webhooks del proveedor de correo)
email_public_routes = APIRouter()


#Envio de mensajes --------------------------------->


@email_routes.get("/email/simple_message", tags=["Email"])
def get_simple_message():
    NAME = "get_simple_message"
    to_users = "almazanmendez@hotmail.com"
    response = send_simple_message("",[to_users],"Comprobante","Hola persona")
    response_json = json.loads(response.text)
    return response_json


@email_routes.get("/email/send_message_attachments", tags=["Email"])
def send_message_attachments():
    NAME = "send_message_attachments"
    to_users = "almazanmendez@hotmail.com"
    files = [
        {
            "nombre":"kirby.jpg",
            "ruta":"media/tmp/kirby.jpg"
        },
        {
            "nombre":"pokenon.jpg",
            "ruta":"media/tmp/allister-y-gengar-de-pokemon-espada-y-escudo_3840x2160_xtrafondos.com.jpg"
        }
    ]
    response = send_attachment_message("",[to_users],"Comprobante","Hola persona",files)
    response_json = json.loads(response.text)
    return response_json


@email_routes.get("/email/send_message_html", tags=["Email"])
def send_message_html():
    NAME = "send_message_html"
    to_users = "almazanmendez@hotmail.com"
    html_body = "<html>HTML version of the body</html>"
    response = send_html_message("",[to_users],"Comprobante","Hola persona",html_body)
    response_json = json.loads(response.text)
    return response_json


@email_routes.get("/email/send_message_schedule", tags=["Email"])
def send_message_schedule():
    NAME = "send_message_schedule"
    to_users = "almazanmendez@hotmail.com"
    html_body = "<html>HTML version of the body</html>"
    date = datetime.now(newMexZone) + timedelta(minutes=5)
    dateformat = date.strftime("%a, %d %b %Y %H:%M:%S %z")
    print(dateformat)
    response = send_scheduled_message("",[to_users],"Comprobante","Hola",dateformat)
    print(response.text)
    response_json = json.loads(response.text)
    return response_json


#Manejo de templates --------------------------------->


@email_routes.get("/email/template_email/create_template", tags=["Email"])
def create_template_for_message_email():
    template_html = """
    <p>Se acaba de registrar <strong>{{user_name}} {{user_lastname_father}} {{user_lastname_mother}}</strong> en el sistema. Debemos pronto recibir un registro de alg&uacute;n hijo o hija con sus apellidos. En caso de que esto no suceda el d&iacute;a de hoy, hay que contactarlos para ver si les podemos ayudar en algo.</p>

    <p>-</p>

    <p>Kin Camp SA de CV</p>
    """
    template_name = "template.example"
    template_description = "Template Example only for integration"
    template_comment = "template for example"
    response = send_create_template(template_html,template_name,template_description,template_comment)
    print(response)
    print(response.text)
    response_json = json.loads(response.text)
    return response_json


@email_routes.get("/email/template_email/get_template", tags=["Email"])
def get_template_for_message_email():
    template_name = "template.example"
    response = get_template(template_name)
    print(response)
    print(response.text)
    response_json = json.loads(response.text)
    return response_json 


@email_routes.get("/email/template_email/update_template", tags=["Email"])
def get_update_template_for_message_email():
    template_name = "template.example"
    response = update_template(template_name)
    print(response)
    print(response.text)
    response_json = json.loads(response.text)
    return response_json 


@email_routes.get("/email/simple_message_with_template", tags=["Email"])
def get_simple_message_with_template():
    NAME = "get_simple_message_with_template"
    to_users = "almazanmendez@hotmail.com"
    response = send_message_by_template_id("",[to_users],"Comprobante")
    response_json = json.loads(response.text)
    return response_json


#Crud de Webhooks --------------------------------->


@email_routes.get("/email/registry_webhook", tags=["Email"])
def get_registry_webhook():
    """
    Regresa toda la informacion de los webhooks registrados
    """
    NAME = "get_registry_webhook"
    response = send_get_webhook()
    response_json = json.loads(response.text)
    return response_json


@email_routes.get("/email/registry_webhook/{webhook_type}", tags=["Email"])
def get_registry_webhook_for_type(webhook_type:str):
    """
    Regresa toda la informacion de un tipo en especifico
    """
    NAME = "get_registry_webhook_for_type"
    arr_types = ["accepted",
        "clicked",
        "complained",
        "delivered",
        "opened",
        "permanent_fail",
        "temporary_fail",
        "unsubscribed"]
    
    if webhook_type not in arr_types:
        response.status_code = 401
        return {"mensaje":"El tipo ingresado no existe"}
    
    response = get_domain(webhook_type)
    response_json = json.loads(response.text)
    return response_json


@email_routes.post("/email/registry_webhook", tags=["Email"])
def create_registry_webhook(email_webhook:EmailWebhookCreate,response: Response):
    """
    Crea un registro para el tipo de webhook con las url's donde se enviara la informacion
    """
    NAME = "create_registry_webhook"
    print(email_webhook.type)
    print(email_webhook.urls)
    arr_types = ["accepted",
        "clicked",
        "complained",
        "delivered",
        "opened",
        "permanent_fail",
        "temporary_fail",
        "unsubscribed"]
    if email_webhook.type not in arr_types:
        response.status_code = 401
        return {"mensaje":"El tipo ingresado no existe"}
    
    if len(email_webhook.urls) > 3:
        response.status_code = 401
        return {"mensaje":"El tamaño del arreglo de urls es mayor a 3"}
    
    # response = add_webhook(email_webhook.type,email_webhook.urls)
    # response_json = json.loads(response.text)
    return [] #response_json


@email_routes.patch("/email/registry_webhook/{webhook_type}", tags=["Email"])
def update_registry_webhook(webhook_type:str,webhook_url:WebhookUrl,response: Response):
    """
    Actualiza las urls para un tipo de webhook
    """
    NAME = "update_registry_webhook"
    arr_types = ["accepted",
        "clicked",
        "complained",
        "delivered",
        "opened",
        "permanent_fail",
        "temporary_fail",
        "unsubscribed"]
    if webhook_type.type not in arr_types:
        response.status_code = 401
        return {"mensaje":"El tipo ingresado no existe"}
    
    if len(webhook_url.urls) > 3:
        response.status_code = 401
        return {"mensaje":"El tamaño del arreglo de urls es mayor a 3"}
    
    # response = update_webhook(webhook_type,webhook_url.urls)
    # response_json = json.loads(response.text)
    return [] #response_json


@email_routes.delete("/email/registry_webhook/{webhook_type}", tags=["Email"])
def delete_registry_webhook(webhook_type:str,response: Response):
    """
    Borra los registros del typo de webhook que se mande
    """
    NAME = "delete_registry_webhook"
    arr_types = ["accepted",
        "clicked",
        "complained",
        "delivered",
        "opened",
        "permanent_fail",
        "temporary_fail",
        "unsubscribed"]
    if webhook_type.type not in arr_types:
        response.status_code = 401
        return {"mensaje":"El tipo ingresado no existe"}
    
    # response = delete_domain(webhook_type)
    # response_json = json.loads(response.text)
    return [] #response_json


#Webhook para los estados de los correos  --------------------------------->


@email_public_routes.post("/email/accepted_webhook", tags=["Email"])
async def listen_accepted_webhook(request: Request):
    NAME = "listen_accepted_webhook"
    datos = await request.body()
    print(datos)
    Ejemplo_request = """
    {
        "signature": {
            "token": "7af1671541e4542a98070f92cc2db17252baed30c2e90f8535",
            "timestamp": "1694738248",
            "signature": "19f70ee9705da8ab2530ec08be35b69a2a97d025cb3a44348ccde57e9dcdfd16"
        },
        "event-data": {
            \n\t"event": "accepted",
            \n\t"id": "nIKIiE5URaSr-8WsuiCrBB",
            \n\t"timestamp": 1521472262.908181,
            \n\t"api-key-id": "aff8axxx-23990xxx",
            \n\t"flags": {
            \n\t\t"is-authenticated": true,
            \n\t\t"is-test-mode": false\n\t
            },
            \n\t"envelope": {
            \n\t\t"transport": "smtp",
            \n\t\t"sender": "bob@cc.camploshuizaches.mx",
            \n\t\t"targets": "alice@example.com"\n\t
            },
            \n\t"message": {
            \n\t\t"headers": {
                \n\t\t\t"to": "Alice <alice@example.com>",
                \n\t\t\t"message-id": "20130503182626.18666.16540@cc.camploshuizaches.mx",
                \n\t\t\t"from": "Bob <bob@cc.camploshuizaches.mx>",
                \n\t\t\t"subject": "Test accepted webhook"\n\t\t
            },
            \n\t\t"attachments": [
                
            ],
            \n\t\t"size": 256\n\t
            },
            \n\t"storage": {
            \n\t\t"url": "https://se.api.mailgun.net/v3/domains/cc.camploshuizaches.mx/messages/message_key",
            \n\t\t"key": "message_key"\n\t
            },
            \n\t"recipient": "alice@example.com",
            \n\t"recipient-domain": "example.com",
            \n\t"method": "HTTP",
            \n\t"log-level": "info",
            \n\t"tags": [
            "my_tag_1",
            "my_tag_2"
            ],
            \n\t"user-variables": {
            \n\t\t"my_var_1": "Mailgun Variable #1",
            \n\t\t"my-var-2": "awesome"\n\t
            }\n
        }
        }
    """
    return []


@email_public_routes.post("/email/clicks_webhook", tags=["Email"])
async def listen_clicks_webhook(request: Request):
    """
    Note When adding a Clicked or Opened webhook, ensure that you also have tracking enabled.
    > En la parte del envio de correos existe un campo tracking asegurarse de que esta en True
      para poder rastrearlo

    Tracking can also be toggled by setting o:tracking, o:tracking-clicks and o:tracking-opens parameters when sending your message. This will override the domain-level setting.
    > Esta configuracion es para los mensajes, se pone aqui con la intencion de que sea destacable que es necesario para que funcionen estos metodos
    """
    NAME = "listen_clicks_webhook"
    datos = await request.body()
    print(datos)
    Ejemplo_request = """
        {
        "signature": {
            "token": "406e5058709048336ca3221486882524a19adcff2e092d2cf1",
            "timestamp": "1694738929",
            "signature": "1b299bc45a2741c464507a7f45c85debdcf056be544ee715f0268bf48593772c"
        },
        "event-data": {
            \n\t"id": "Ase7i2zsRYeDXztHGENqRA",
            \n\t"timestamp": 1521243339.873676,
            \n\t"log-level": "info",
            \n\t"event": "clicked",
            \n\t"message": {
            \n\t\t"headers": {
                \n\t\t\t"message-id": "20130503182626.18666.16540@cc.camploshuizaches.mx"\n\t\t
            }\n\t
            },
            \n\t"recipient": "alice@example.com",
            \n\t"recipient-domain": "example.com",
            \n\t"ip": "50.56.129.169",
            \n\t"geolocation": {
            \n\t\t"country": "US",
            \n\t\t"region": "CA",
            \n\t\t"city": "San Francisco"\n\t
            },
            \n\t"client-info": {
            \n\t\t"client-os": "Linux",
            \n\t\t"device-type": "desktop",
            \n\t\t"client-name": "Chrome",
            \n\t\t"client-type": "browser",
            \n\t\t"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31"\n\t
            },
            \n\t"campaigns": [
            
            ],
            \n\t"tags": [
            "my_tag_1",
            "my_tag_2"
            ],
            \n\t"user-variables": {
            \n\t\t"my_var_1": "Mailgun Variable #1",
            \n\t\t"my-var-2": "awesome"\n\t
            }\n
        }
        }
    """
    return []


@email_public_routes.post("/email/delivered_message_webhook", tags=["Email"])
async def listen_delivered_message_webhook(request: Request):
    NAME = "listen_delivered_message_webhook"
    datos = await request.body()
    print(datos)
    Ejemplo_request = """
        {
        "signature": {
            "token": "4e7cd73c38b9242c0eb4dbe02e385a2f6f42d8b26d4b2a2740",
            "timestamp": "1694739120",
            "signature": "f2629d0a4e60a6c569a9fcd97020e54973bf033591bf753b1d7cd3240f6a6ddc"
        },
        "event-data": {
            \n\t"id": "CPgfbmQMTCKtHW6uIWtuVe",
            \n\t"timestamp": 1521472262.908181,
            \n\t"log-level": "info",
            \n\t"event": "delivered",
            \n\t"delivery-status": {
            \n\t\t"tls": true,
            \n\t\t"mx-host": "smtp-in.example.com",
            \n\t\t"code": 250,
            \n\t\t"description": "",
            \n\t\t"session-seconds": 0.4331989288330078,
            \n\t\t"utf8": true,
            \n\t\t"attempt-no": 1,
            \n\t\t"message": "OK",
            \n\t\t"certificate-verified": true\n\t
            },
            \n\t"flags": {
            \n\t\t"is-routed": false,
            \n\t\t"is-authenticated": true,
            \n\t\t"is-system-test": false,
            \n\t\t"is-test-mode": false\n\t
            },
            \n\t"envelope": {
            \n\t\t"transport": "smtp",
            \n\t\t"sender": "bob@cc.camploshuizaches.mx",
            \n\t\t"sending-ip": "209.61.154.250",
            \n\t\t"targets": "alice@example.com"\n\t
            },
            \n\t"message": {
            \n\t\t"headers": {
                \n\t\t\t"to": "Alice <alice@example.com>",
                \n\t\t\t"message-id": "20130503182626.18666.16540@cc.camploshuizaches.mx",
                \n\t\t\t"from": "Bob <bob@cc.camploshuizaches.mx>",
                \n\t\t\t"subject": "Test delivered webhook"\n\t\t
            },
            \n\t\t"attachments": [
                
            ],
            \n\t\t"size": 111\n\t
            },
            \n\t"recipient": "alice@example.com",
            \n\t"recipient-domain": "example.com",
            \n\t"storage": {
            \n\t\t"url": "https://se.api.mailgun.net/v3/domains/cc.camploshuizaches.mx/messages/message_key",
            \n\t\t"key": "message_key"\n\t
            },
            \n\t"campaigns": [
            
            ],
            \n\t"tags": [
            "my_tag_1",
            "my_tag_2"
            ],
            \n\t"user-variables": {
            \n\t\t"my_var_1": "Mailgun Variable #1",
            \n\t\t"my-var-2": "awesome"\n\t
            }\n
        }
        }
    """
    return []


@email_public_routes.post("/email/opens_message_webhook", tags=["Email"])
async def listen_opens_message_webhook(request: Request):
    """
    Note When adding a Clicked or Opened webhook, ensure that you also have tracking enabled.
    > En la parte del envio de correos existe un campo tracking asegurarse de que esta en True
      para poder rastrearlo

    Tracking can also be toggled by setting o:tracking, o:tracking-clicks and o:tracking-opens parameters when sending your message. This will override the domain-level setting.
    > Esta configuracion es para los mensajes, se pone aqui con la intencion de que sea destacable que es necesario para que funcionen estos metodos
    """
    NAME = "listen_opens_message_webhook"
    datos = await request.body()
    print(datos)
    Ejemplo_request = """
        {
        "signature": {
            "token": "a35ff98406784b2e8d756939ca1039fbe6f4b8123c93f0432d",
            "timestamp": "1694739401",
            "signature": "8affa059e2ef3e2d7d6e66d94fae2e2cab537bf98d934ca5fc1e21e2aba55366"
        },
        "event-data": {
            \n\t"id": "Ase7i2zsRYeDXztHGENqRA",
            \n\t"timestamp": 1521243339.873676,
            \n\t"log-level": "info",
            \n\t"event": "opened",
            \n\t"message": {
            \n\t\t"headers": {
                \n\t\t\t"message-id": "20130503182626.18666.16540@cc.camploshuizaches.mx"\n\t\t
            }\n\t
            },
            \n\t"recipient": "alice@example.com",
            \n\t"recipient-domain": "example.com",
            \n\t"ip": "50.56.129.169",
            \n\t"geolocation": {
            \n\t\t"country": "US",
            \n\t\t"region": "CA",
            \n\t\t"city": "San Francisco"\n\t
            },
            \n\t"client-info": {
            \n\t\t"client-os": "Linux",
            \n\t\t"device-type": "desktop",
            \n\t\t"client-name": "Chrome",
            \n\t\t"client-type": "browser",
            \n\t\t"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31"\n\t
            },
            \n\t"campaigns": [
            
            ],
            \n\t"tags": [
            "my_tag_1",
            "my_tag_2"
            ],
            \n\t"user-variables": {
            \n\t\t"my_var_1": "Mailgun Variable #1",
            \n\t\t"my-var-2": "awesome"\n\t
            }\n
        }
        }
    """
    return []
