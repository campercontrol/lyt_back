import jinja2
import requests
import json
import os

domain_name = os.getenv("DOMAIN_NAME", "lytcamp.com.mx")
MAILGUN_SENDING_KEY = os.getenv("MAILGUN_SENDING_KEY")


from_user_email = "Lago y Tierra <contacto@lytcamp.org.mx>"
to_user_email = ""


"""
En caso de requerir una propiedad todavia mas especifica, revisar las siguientes Url
Documentacion General:
    - https://documentation.mailgun.com/en/latest/api_reference.html
Mensajeria:
    - https://documentation.mailgun.com/en/latest/api-sending.html#sending
Templates:
    - https://documentation.mailgun.com/en/latest/api-templates.html#store-new-template
Webhooks:
    - https://documentation.mailgun.com/en/latest/api-webhooks.html#webhooks
    - Existe un formulario donde probar los webhook dentro del dashboard de mailgun
        > Ingresar a la cuenta.
        > Lado izquierdo 'Webhooks'
        > Parte inferior 'Test Webhook'
"""

 
def send_simple_message_test():
    return requests.post(
        f"https://api.mailgun.net/v3/{domain_name}/messages",
        auth=("api", MAILGUN_SENDING_KEY),
        data={"from": from_user_email,
              "to": [to_user_email],
              "subject": "Welcome",
              "text": "Testing some Mailgun awesomness!"})

def send_simple_message(from_user:str,to_users:list,email_subject:str,text_message:str) -> dict:
    """
    Envia un correo simple solo mensaje de texto
    
        "o:tracking":True,
        "o:tracking-clicks":True,
        "o:tracking-opens":True

    Estas opciones son requeridas para el rastreo de mensaje en los webhooks 
    habilitar 
    {{content}}
    {{title}}

    """
    context = {
        "content":text_message,
        "title":email_subject
    }
    template_loader = jinja2.FileSystemLoader('media/')
    template_env= jinja2.Environment(loader = template_loader)

    html_info_camper = 'email.html' #Nombre del template que se usa el html 

    template = template_env.get_template(html_info_camper)
 
    html_content = template.render(context)
    return requests.post(
        f"https://api.mailgun.net/v3/{domain_name}/messages",
        auth=("api", MAILGUN_SENDING_KEY),
        data={"from": from_user_email,
              "to": to_users,
              "subject": email_subject,
              "html": html_content,
              "o:tracking":True,
              "o:tracking-clicks":True,
              "o:tracking-opens":True,
              "o:tag": ["Tag1", "Tag2"]
              }
    )

def send_attachment_message(from_user:str,to_users:list,email_subject:str,text_message:str,attachments_list:list):
    """Envia correo con multiples archivos"""
    attachments = []
    for element in attachments_list:
        attachments.append(("attachment", (element["nombre"], open(element["ruta"],"rb").read())))
    return requests.post(
        f"https://api.mailgun.net/v3/{domain_name}/messages",
        auth=("api", MAILGUN_SENDING_KEY), 
        files=attachments,
        data={"from": from_user_email,
              "to": to_users,
              "subject": email_subject,
              "text": text_message
              }
        )

def send_html_message(from_user:str,to_users:list,email_subject:str,text_message:str,html_body:str):
    """Envia un correo con un html"""
    #A considerar la propiedad text y html solo se puede enviar uno 
    #text : Texto plano
    #html : html 
    #en caso de enviar los dos da prioridad al HTML y el text no lo muestra
    return requests.post(
        f"https://api.mailgun.net/v3/{domain_name}/messages",
        auth=("api", MAILGUN_SENDING_KEY),
        data={"from": from_user_email,
              "to": to_users,
              "subject": email_subject,
              "text": text_message,
              "html":html_body
              }
        )

def send_scheduled_message(from_user:str,to_users:list,email_subject:str,text_message:str,date:str):
    """Enviar un correo en una fecha y hora especifica"""
    #Consideraciones solo se puede enviar el mensaje 3 dias mas despues de la fecha de envio

    return requests.post(
        f"https://api.mailgun.net/v3/{domain_name}/messages",
        auth=("api", MAILGUN_SENDING_KEY),
        data={"from": from_user_email,
              "to": to_users,
              "subject": email_subject,
              "text": text_message,
              "o:deliverytime": date})
                              # "Fri, 18 Aug 2023 09:15:39 625264"

#Limitaciones para templates
# - 100 templates per domain
# - 10 versions per template
# - 100Kb max template size

def send_create_template(template_html:str,template_name:str,template_description:str,template_comment:str):
    """Crea un registro de template para un mensaje en HTML 
        los parametros deben estar especificadas con dobles llaves {{var}}
    """
    return requests.post(
        f"https://api.mailgun.net/v3/{domain_name}/templates",
        auth=("api", MAILGUN_SENDING_KEY),
        data={'name': template_name,
              'description': template_description,
              'template': template_html,
              'engine': 'handlebars',
              'comment': template_comment
              })
    
def get_template(template_name:str):
    return requests.get(
        f"https://api.mailgun.net/v3/{domain_name}/templates/{template_name}",
        auth=("api", MAILGUN_SENDING_KEY),
        params={"active": "yes"})

def update_template(template_name:str):
    return requests.put(
        f"https://api.mailgun.net/v3/{domain_name}/templates/{template_name}",
        auth=('api', MAILGUN_SENDING_KEY),
        data={'description': 'Template Example only for integration modify'})

def send_message_by_template_id(from_user:str,to_users:list,email_subject:str):
    return requests.post(
        f"https://api.mailgun.net/v3/{domain_name}/messages",
        auth=("api", MAILGUN_SENDING_KEY),
        data={"from": from_user_email,
              "to": to_users,
              "subject": email_subject,
              "template": "template.example",
              "h:X-Mailgun-Variables": json.dumps({
                  "user_name": "people", 
                  "user_lastname_father": "apellido1",
                  "user_lastname_mother": "apellido2"
                  })
              }
        )
    # return requests.post(
    #     f"https://api.mailgun.net/v3/{domain_name}/messages",
    #     auth=("api", MAILGUN_SENDING_KEY),
    #     data={"from": from_user_email,
    #           "to": to_users,
    #           "subject": email_subject,
    #           "template": "template.example",
    #           "t:variables": json.dumps({
    #               "user_name": "people", 
    #               "user_lastname_father": "apellido1",
    #               "user_lastname_mother": "apellido2"
    #               }) 
    #           }
    #     )


def send_get_webhook():
    return requests.get(
        f"https://api.mailgun.net/v3/domains/{domain_name}/webhooks",
        auth=("api", MAILGUN_SENDING_KEY))


def get_domain(type_webhook):
    return requests.get(
        f"https://api.mailgun.net/v3/domains/{domain_name}/webhooks/{type_webhook}",
        auth=("api", MAILGUN_SENDING_KEY))


def add_webhook(webhook_type,urls):
    types_webhook="""   
        accepted
        clicked
        complained
        delivered
        opened
        permanent_fail
        temporary_fail
        unsubscribed
    """
    return requests.post(
        f"https://api.mailgun.net/v3/domains/{domain_name}/webhooks",
        auth=("api", MAILGUN_SENDING_KEY),
        data={
          'id':webhook_type,
          'url':urls
        })


def update_webhook(type_webhook,arr_url):
    return requests.put(
        (f"https://api.mailgun.net/v3/domains/{domain_name}/webhooks/{type_webhook}"),
        auth=('api', MAILGUN_SENDING_KEY),
        data={'url': arr_url})


def delete_domain(type_webhook):
    return requests.delete(
        f"https://api.mailgun.net/v3/domains/{domain_name}/webhooks/{type_webhook}",
        auth=("api", MAILGUN_SENDING_KEY))
