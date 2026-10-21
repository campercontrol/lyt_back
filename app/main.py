import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from service.prueba_service import prueba_routes
from datetime import datetime, timezone
from service.catalogs.currency_service import currency_routes
from service.catalogs.vaccine_service import vaccine_routes
from service.catalogs.food_restriction_service import food_restriction_routes
from service.catalogs.licensed_medicine_service import licensed_medicine_routes
from service.catalogs.pathological_back_fm_service import pathological_background_family_routes
from service.catalogs.pathological_back_service import pathological_background_routes
from service.catalogs.constant_service import constant_routes
from service.catalogs.payment_account_service  import payment_account_routes
from service.catalogs.staff_role_service import staff_role_routes
from service.campers.school_service import school_routes
from service.campers.parent_service import parent_routes, parent_public_routes
from service.campers.camper_service import camper_routes, camper_public_routes
from service.camps.location_service import location_routes
from service.camps.season_service import season_routes
from service.camps.camp_service import camp_router
from service.camps.camp_extra_charge_service import extra_charge_routes
from service.camps.camp_extra_question_service import extra_question_routes
from service.campers.camper_extra_question_service import extra_answer_routes
from service.campers.camper_comment_service import camper_comment_router
from service.camps.camp_checkpoint_service import camp_checkpoint_routes
from service.campers.camper_checkpoint_service import camper_checkpoint_routes
from service.payments.payment_service import payment_routes
from service.payments.payment_method_service import payment_method_routes
from service.payments.payment_transaction_type_service import payment_transaction_type_routes
from service.payments.camper_extra_charge_service import camper_extra_charge_routes
from service.staffs.staff_service import staff_routes, staff_public_routes
from service.camps.staff_in_camp_service import staff_in_camp_routes
from service.training.training_service import training_router
from service.training.training_event_service import training_event_router
from service.training.staff_in_training_service import staff_in_training_router
from service.file import files_routes
from service.campers.camper_record_service import camper_record_routes
from service.staffs.staff_record_service import staff_record_routes
from service.staffs.staff_comment_service import staff_comment_routes
from service.mailings.email_template_service import email_template_routes
from service.mailings.campaign_service import campaign_routes
from service.mailings.mailing_service import mailing_routes
from service.camps.report_service import report_routes
from service.trophies.trophy_service import trophy_routes
from service.trophies.trophy_season_service import trophy_season_routes
from service.trophies.trophy_staff_service import trophy_staff_routes
from service.medical.medical_service import medical_routes
from service.mercadopago.mercado_pago_service import mercadopago_routes, mercadopago_public_routes
from service.role import role_routes
from service.user import user_routes, user_public_routes
# from service.token import token_routes
# Temporal Token Fix, please uncomment this code in the next iteration
from service.auth.auth_service import token_routes
from service.image import image_routes
from service.permission import permission_routes
from service.generar_pdf import pdf_routes
from service.email import email_routes, email_public_routes
from service.groupings.grouping_service import grouping_router
from service.groupings.grouping_type_service import grouping_type_router
from service.groupings.grouping_camp_service import grouping_camp_router
from service.groupings.grouping_camper_service import grouping_camper_router
from fastapi.staticfiles import StaticFiles
from crud.auth.auth_crud import get_current_user
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from cron_scripts.camper_birthday_greetings import main as send_birthday_greetings

user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db = os.getenv("DB_NAME")


DB_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
app = FastAPI()

auth_user = [Depends(get_current_user)]


# Configure job store
jobstores = {
    "default": SQLAlchemyJobStore(url=DB_URL)
}

scheduler = BackgroundScheduler(jobstores=jobstores)

origins = ["http://localhost:4200",
           "http://localhost",
           "http://localhost:8080",
           "http://app.campercontrol.com",
           "https://app.campercontrol.com",
           "http://migracion.campercontrol.com"
           ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Routers protegidos: requieren header "Authorization: Bearer <token>"
app.include_router(prueba_routes, dependencies=auth_user)  # Login
app.include_router(currency_routes, dependencies=auth_user)
app.include_router(vaccine_routes, dependencies=auth_user)
app.include_router(food_restriction_routes, dependencies=auth_user)
app.include_router(licensed_medicine_routes, dependencies=auth_user)
app.include_router(pathological_background_routes, dependencies=auth_user)
app.include_router(pathological_background_family_routes, dependencies=auth_user)
app.include_router(constant_routes, dependencies=auth_user)
app.include_router(payment_account_routes, dependencies=auth_user)
app.include_router(staff_role_routes, dependencies=auth_user)
app.include_router(school_routes, dependencies=auth_user)
app.include_router(parent_routes, dependencies=auth_user)
app.include_router(camper_routes, dependencies=auth_user)
app.include_router(location_routes, dependencies=auth_user)
app.include_router(season_routes, dependencies=auth_user)
app.include_router(camp_router, dependencies=auth_user)
app.include_router(extra_charge_routes, dependencies=auth_user)
app.include_router(extra_question_routes, dependencies=auth_user)
app.include_router(extra_answer_routes, dependencies=auth_user)
app.include_router(camper_comment_router, dependencies=auth_user)
app.include_router(camp_checkpoint_routes, dependencies=auth_user)
app.include_router(camper_checkpoint_routes, dependencies=auth_user)
app.include_router(payment_routes, dependencies=auth_user)
app.include_router(payment_method_routes, dependencies=auth_user)
app.include_router(payment_transaction_type_routes, dependencies=auth_user)
app.include_router(camper_extra_charge_routes, dependencies=auth_user)
app.include_router(staff_routes, dependencies=auth_user)
app.include_router(staff_in_camp_routes, dependencies=auth_user)
app.include_router(training_router, dependencies=auth_user)
app.include_router(training_event_router, dependencies=auth_user)
app.include_router(staff_in_training_router, dependencies=auth_user)
app.include_router(camper_record_routes, dependencies=auth_user)
app.include_router(staff_record_routes, dependencies=auth_user)
app.include_router(staff_comment_routes, dependencies=auth_user)
app.include_router(email_template_routes, dependencies=auth_user)
app.include_router(campaign_routes, dependencies=auth_user)
app.include_router(mailing_routes, dependencies=auth_user)
app.include_router(report_routes, dependencies=auth_user)
app.include_router(trophy_routes, dependencies=auth_user)
app.include_router(trophy_season_routes, dependencies=auth_user)
app.include_router(trophy_staff_routes, dependencies=auth_user)
app.include_router(medical_routes, dependencies=auth_user)
app.include_router(role_routes, dependencies=auth_user) # Role
app.include_router(user_routes, dependencies=auth_user) # User
app.include_router(permission_routes, dependencies=auth_user) # Permission
app.include_router(pdf_routes, dependencies=auth_user) #Pdf
app.include_router(mercadopago_routes, dependencies=auth_user)
app.include_router(grouping_router, dependencies=auth_user)
app.include_router(grouping_type_router, dependencies=auth_user)
app.include_router(grouping_camp_router, dependencies=auth_user)
app.include_router(grouping_camper_router, dependencies=auth_user)
app.include_router(email_routes, dependencies=auth_user) #email

# Routers publicos: login, registro, recuperacion de cuenta, webhooks y archivos
app.include_router(token_routes) # token
app.include_router(user_public_routes)
app.include_router(parent_public_routes)
app.include_router(staff_public_routes)
app.include_router(camper_public_routes)
app.include_router(mercadopago_public_routes)
app.include_router(email_public_routes)
app.include_router(files_routes)
app.include_router(image_routes) # Image
app.mount("/media",StaticFiles(directory="media"),name="media")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# @app.on_event("startup")
# def start_scheduler():
#     scheduler.start()
#     # Schedule job if not already present
#     if not scheduler.get_job("birthday_greeting_job"):
#         print("Adding Job")
#         scheduler.add_job(
#             send_birthday_greetings,
#             trigger="cron",
#             hour="15",
#             minute="0",
#             id="birthday_greeting_job",
#             replace_existing=True,
#             misfire_grace_time=3600  # 1 hour grace period
#         )
#     print("Scheduler started at", datetime.now())



@app.get("/remove_job/", tags=["Jobs"], dependencies=auth_user)
def get_prospects():
    result = scheduler.remove_job("birthday_greeting_job")
    print("Job removed:", result)
    
@app.get("/jobs", tags=["Jobs"], dependencies=auth_user)
def list_jobs():
    """
    List all scheduled jobs (for debugging).
    Shows next run times and job IDs.
    """
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time),
            "trigger": str(job.trigger)
        })
    return {"jobs": jobs}

@app.post("/run-birthday-job", tags=["Jobs"], dependencies=auth_user)
def run_birthday_job():
    """
    Manually trigger the birthday greetings job.
    Useful for testing without waiting for the schedule.
    """
    try:
        send_birthday_greetings()
        return {"status": "Birthday greetings job executed successfully"}
    except Exception as e:
        return {"status": "Error executing job", "error": str(e)}