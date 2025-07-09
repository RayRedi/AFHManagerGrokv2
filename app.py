import os
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, send_file, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user, current_user
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, IntegerField, HiddenField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from flask_mail import Mail, Message
import re
import json
from cryptography.fernet import Fernet
from sqlalchemy import TypeDecorator, Text
from sqlalchemy.ext.hybrid import hybrid_property
import sqlite3
# Initialize Flask app
app = Flask(__name__)
def init_medications():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL,
            generic_name TEXT NOT NULL,
            common_uses TEXT
        )
    ''')
    conn.commit()

    # Add sample data only if empty
    c.execute('SELECT COUNT(*) FROM medications')
    if c.fetchone()[0] == 0:
        elderly_meds = [
            # Cardiovascular medications
            ('Lipitor', 'Atorvastatin', 'High cholesterol, cardiovascular disease prevention'),
            ('Crestor', 'Rosuvastatin', 'High cholesterol, heart disease prevention'),
            ('Zocor', 'Simvastatin', 'High cholesterol'),
            ('Pravachol', 'Pravastatin', 'High cholesterol'),
            ('Livalo', 'Pitavastatin', 'High cholesterol'),
            ('Lisinopril', 'Lisinopril', 'High blood pressure, heart failure'),
            ('Norvasc', 'Amlodipine', 'High blood pressure, angina'),
            ('Lotrel', 'Amlodipine/Benazepril', 'High blood pressure'),
            ('Toprol XL', 'Metoprolol', 'High blood pressure, heart failure'),
            ('Coreg', 'Carvedilol', 'Heart failure, high blood pressure'),
            ('Losartan', 'Losartan', 'High blood pressure'),
            ('Valsartan', 'Valsartan', 'High blood pressure, heart failure'),
            ('Diovan', 'Valsartan', 'High blood pressure, heart failure'),
            ('Cozaar', 'Losartan', 'High blood pressure'),
            ('Avapro', 'Irbesartan', 'High blood pressure'),
            ('Atacand', 'Candesartan', 'High blood pressure'),
            ('Micardis', 'Telmisartan', 'High blood pressure'),
            ('Benicar', 'Olmesartan', 'High blood pressure'),
            ('Prinivil', 'Lisinopril', 'High blood pressure, heart failure'),
            ('Zestril', 'Lisinopril', 'High blood pressure, heart failure'),
            ('Altace', 'Ramipril', 'High blood pressure, heart failure'),
            ('Vasotec', 'Enalapril', 'High blood pressure, heart failure'),
            ('Capoten', 'Captopril', 'High blood pressure, heart failure'),
            ('Monopril', 'Fosinopril', 'High blood pressure'),
            ('Accupril', 'Quinapril', 'High blood pressure'),
            ('Univasc', 'Moexipril', 'High blood pressure'),
            ('Mavik', 'Trandolapril', 'High blood pressure'),
            ('Plavix', 'Clopidogrel', 'Blood clot prevention'),
            ('Coumadin', 'Warfarin', 'Blood clot prevention'),
            ('Eliquis', 'Apixaban', 'Blood clot prevention, atrial fibrillation'),
            ('Xarelto', 'Rivaroxaban', 'Blood clot prevention'),
            ('Pradaxa', 'Dabigatran', 'Blood clot prevention, atrial fibrillation'),
            ('Savaysa', 'Edoxaban', 'Blood clot prevention'),
            ('Brilinta', 'Ticagrelor', 'Blood clot prevention'),
            ('Effient', 'Prasugrel', 'Blood clot prevention'),
            ('Lanoxin', 'Digoxin', 'Heart failure, atrial fibrillation'),
            ('Tambocor', 'Flecainide', 'Irregular heartbeat'),
            ('Rythmol', 'Propafenone', 'Irregular heartbeat'),
            ('Multaq', 'Dronedarone', 'Atrial fibrillation'),
            ('Tikosyn', 'Dofetilide', 'Atrial fibrillation'),
            ('Cordarone', 'Amiodarone', 'Irregular heartbeat'),
            ('Pacerone', 'Amiodarone', 'Irregular heartbeat'),
            ('Sotalol', 'Sotalol', 'Irregular heartbeat'),
            ('Betapace', 'Sotalol', 'Irregular heartbeat'),
            ('Quinidine', 'Quinidine', 'Irregular heartbeat'),
            ('Procainamide', 'Procainamide', 'Irregular heartbeat'),
            ('Disopyramide', 'Disopyramide', 'Irregular heartbeat'),
            ('Propranolol', 'Propranolol', 'High blood pressure, heart rhythm'),
            ('Inderal', 'Propranolol', 'High blood pressure, migraine prevention'),
            ('Tenormin', 'Atenolol', 'High blood pressure'),
            ('Lopressor', 'Metoprolol', 'High blood pressure, heart failure'),
            ('Zebeta', 'Bisoprolol', 'Heart failure'),
            ('Bystolic', 'Nebivolol', 'High blood pressure'),
            ('Sectral', 'Acebutolol', 'High blood pressure'),
            ('Kerlone', 'Betaxolol', 'High blood pressure'),
            ('Levatol', 'Penbutolol', 'High blood pressure'),
            ('Visken', 'Pindolol', 'High blood pressure'),
            ('Blocadren', 'Timolol', 'High blood pressure'),
            ('Corgard', 'Nadolol', 'High blood pressure'),
            ('Trandate', 'Labetalol', 'High blood pressure'),
            ('Normodyne', 'Labetalol', 'High blood pressure'),
            ('Cardura', 'Doxazosin', 'High blood pressure, enlarged prostate'),
            ('Hytrin', 'Terazosin', 'High blood pressure, enlarged prostate'),
            ('Minipress', 'Prazosin', 'High blood pressure'),
            ('Uroxatral', 'Alfuzosin', 'Enlarged prostate'),
            ('Flomax', 'Tamsulosin', 'Enlarged prostate'),
            ('Rapaflo', 'Silodosin', 'Enlarged prostate'),
            ('Catapres', 'Clonidine', 'High blood pressure'),
            ('Tenex', 'Guanfacine', 'High blood pressure'),
            ('Wytensin', 'Guanabenz', 'High blood pressure'),
            ('Methyldopa', 'Methyldopa', 'High blood pressure'),
            ('Aldactone', 'Spironolactone', 'Heart failure, high blood pressure'),
            ('Inspra', 'Eplerenone', 'Heart failure, high blood pressure'),
            ('Lasix', 'Furosemide', 'Fluid retention, heart failure'),
            ('Bumex', 'Bumetanide', 'Fluid retention'),
            ('Demadex', 'Torsemide', 'Fluid retention'),
            ('Edecrin', 'Ethacrynic acid', 'Fluid retention'),
            ('Hydrochlorothiazide', 'Hydrochlorothiazide', 'High blood pressure, fluid retention'),
            ('Microzide', 'Hydrochlorothiazide', 'High blood pressure'),
            ('Chlorthalidone', 'Chlorthalidone', 'High blood pressure'),
            ('Indapamide', 'Indapamide', 'High blood pressure'),
            ('Zaroxolyn', 'Metolazone', 'Fluid retention'),
            ('Midamor', 'Amiloride', 'Fluid retention'),
            ('Dyrenium', 'Triamterene', 'Fluid retention'),
            ('Maxzide', 'Triamterene/HCTZ', 'High blood pressure'),
            ('Dyazide', 'Triamterene/HCTZ', 'High blood pressure'),
            ('Aldactazide', 'Spironolactone/HCTZ', 'High blood pressure'),
            ('Nitrostat', 'Nitroglycerin', 'Chest pain, angina'),
            ('Imdur', 'Isosorbide mononitrate', 'Chest pain prevention'),
            ('Isordil', 'Isosorbide dinitrate', 'Chest pain prevention'),
            ('Ranexa', 'Ranolazine', 'Chronic angina'),
            ('Norpace', 'Disopyramide', 'Heart rhythm disorders'),
            ('Vasodilan', 'Isoxsuprine', 'Circulation problems'),
            ('Pentoxifylline', 'Pentoxifylline', 'Circulation problems'),
            ('Pletal', 'Cilostazol', 'Circulation problems'),

            # Diabetes medications
            ('Metformin', 'Metformin', 'Type 2 diabetes'),
            ('Glucophage', 'Metformin', 'Type 2 diabetes'),
            ('Januvia', 'Sitagliptin', 'Type 2 diabetes'),
            ('Onglyza', 'Saxagliptin', 'Type 2 diabetes'),
            ('Tradjenta', 'Linagliptin', 'Type 2 diabetes'),
            ('Nesina', 'Alogliptin', 'Type 2 diabetes'),
            ('Invokana', 'Canagliflozin', 'Type 2 diabetes'),
            ('Farxiga', 'Dapagliflozin', 'Type 2 diabetes'),
            ('Jardiance', 'Empagliflozin', 'Type 2 diabetes, heart failure'),
            ('Steglatro', 'Ertugliflozin', 'Type 2 diabetes'),
            ('Amaryl', 'Glimepiride', 'Type 2 diabetes'),
            ('Glucotrol', 'Glipizide', 'Type 2 diabetes'),
            ('Micronase', 'Glyburide', 'Type 2 diabetes'),
            ('DiaBeta', 'Glyburide', 'Type 2 diabetes'),
            ('Glynase', 'Glyburide', 'Type 2 diabetes'),
            ('Prandin', 'Repaglinide', 'Type 2 diabetes'),
            ('Starlix', 'Nateglinide', 'Type 2 diabetes'),
            ('Actos', 'Pioglitazone', 'Type 2 diabetes'),
            ('Avandia', 'Rosiglitazone', 'Type 2 diabetes'),
            ('Precose', 'Acarbose', 'Type 2 diabetes'),
            ('Glyset', 'Miglitol', 'Type 2 diabetes'),
            ('Insulin', 'Insulin', 'Type 1 and 2 diabetes'),
            ('Lantus', 'Insulin glargine', 'Long-acting insulin'),
            ('Levemir', 'Insulin detemir', 'Long-acting insulin'),
            ('Toujeo', 'Insulin glargine', 'Long-acting insulin'),
            ('Tresiba', 'Insulin degludec', 'Long-acting insulin'),
            ('Humalog', 'Insulin lispro', 'Fast-acting insulin'),
            ('Novolog', 'Insulin aspart', 'Fast-acting insulin'),
            ('Apidra', 'Insulin glulisine', 'Fast-acting insulin'),
            ('Fiasp', 'Insulin aspart', 'Fast-acting insulin'),
            ('Humulin', 'Human insulin', 'Diabetes'),
            ('Novolin', 'Human insulin', 'Diabetes'),
            ('Victoza', 'Liraglutide', 'Type 2 diabetes'),
            ('Ozempic', 'Semaglutide', 'Type 2 diabetes'),
            ('Trulicity', 'Dulaglutide', 'Type 2 diabetes'),
            ('Bydureon', 'Exenatide', 'Type 2 diabetes'),
            ('Byetta', 'Exenatide', 'Type 2 diabetes'),
            ('Symlinpen', 'Pramlintide', 'Diabetes'),

            # Bone health medications
            ('Fosamax', 'Alendronate', 'Osteoporosis'),
            ('Actonel', 'Risedronate', 'Osteoporosis'),
            ('Boniva', 'Ibandronate', 'Osteoporosis'),
            ('Reclast', 'Zoledronic acid', 'Osteoporosis'),
            ('Atelvia', 'Risedronate', 'Osteoporosis'),
            ('Binosto', 'Alendronate', 'Osteoporosis'),
            ('Prolia', 'Denosumab', 'Osteoporosis'),
            ('Forteo', 'Teriparatide', 'Osteoporosis'),
            ('Tymlos', 'Abaloparatide', 'Osteoporosis'),
            ('Evenity', 'Romosozumab', 'Osteoporosis'),
            ('Miacalcin', 'Calcitonin', 'Osteoporosis'),
            ('Fortical', 'Calcitonin', 'Osteoporosis'),
            ('Raloxifene', 'Raloxifene', 'Osteoporosis'),
            ('Evista', 'Raloxifene', 'Osteoporosis'),

            # Pain and inflammation medications
            ('Tylenol', 'Acetaminophen', 'Pain relief, fever'),
            ('Advil', 'Ibuprofen', 'Pain, inflammation, fever'),
            ('Motrin', 'Ibuprofen', 'Pain, inflammation, fever'),
            ('Aleve', 'Naproxen', 'Pain, inflammation'),
            ('Naprosyn', 'Naproxen', 'Pain, inflammation'),
            ('Anaprox', 'Naproxen', 'Pain, inflammation'),
            ('Celebrex', 'Celecoxib', 'Arthritis pain, inflammation'),
            ('Voltaren', 'Diclofenac', 'Arthritis pain, inflammation'),
            ('Mobic', 'Meloxicam', 'Arthritis pain, inflammation'),
            ('Indocin', 'Indomethacin', 'Arthritis, inflammation'),
            ('Relafen', 'Nabumetone', 'Arthritis'),
            ('Feldene', 'Piroxicam', 'Arthritis'),
            ('Lodine', 'Etodolac', 'Arthritis'),
            ('Daypro', 'Oxaprozin', 'Arthritis'),
            ('Clinoril', 'Sulindac', 'Arthritis'),
            ('Tolectin', 'Tolmetin', 'Arthritis'),
            ('Ansaid', 'Flurbiprofen', 'Arthritis'),
            ('Orudis', 'Ketoprofen', 'Arthritis'),
            ('Actron', 'Ketoprofen', 'Pain, inflammation'),
            ('Arthrotec', 'Diclofenac/Misoprostol', 'Arthritis'),
            ('Aspirin', 'Aspirin', 'Pain, inflammation, heart protection'),
            ('Ecotrin', 'Aspirin', 'Heart protection, pain'),
            ('Bufferin', 'Aspirin', 'Pain relief'),
            ('Excedrin', 'Aspirin/Acetaminophen/Caffeine', 'Headache, pain'),

            # Mental health medications
            ('Prozac', 'Fluoxetine', 'Depression, anxiety'),
            ('Zoloft', 'Sertraline', 'Depression, anxiety'),
            ('Paxil', 'Paroxetine', 'Depression, anxiety'),
            ('Lexapro', 'Escitalopram', 'Depression, anxiety'),
            ('Celexa', 'Citalopram', 'Depression'),
            ('Effexor', 'Venlafaxine', 'Depression, anxiety'),
            ('Cymbalta', 'Duloxetine', 'Depression, anxiety, neuropathy'),
            ('Pristiq', 'Desvenlafaxine', 'Depression'),
            ('Wellbutrin', 'Bupropion', 'Depression, smoking cessation'),
            ('Zyban', 'Bupropion', 'Smoking cessation'),
            ('Remeron', 'Mirtazapine', 'Depression'),
            ('Desyrel', 'Trazodone', 'Depression, insomnia'),
            ('Elavil', 'Amitriptyline', 'Depression, neuropathy'),
            ('Pamelor', 'Nortriptyline', 'Depression'),
            ('Sinequan', 'Doxepin', 'Depression, anxiety'),
            ('Norpramin', 'Desipramine', 'Depression'),
            ('Aventyl', 'Nortriptyline', 'Depression'),
            ('Vivactil', 'Protriptyline', 'Depression'),
            ('Surmontil', 'Trimipramine', 'Depression'),
            ('Anafranil', 'Clomipramine', 'OCD, depression'),
            ('Nardil', 'Phenelzine', 'Depression'),
            ('Parnate', 'Tranylcypromine', 'Depression'),
            ('Marplan', 'Isocarboxazid', 'Depression'),
            ('Emsam', 'Selegiline', 'Depression'),
            ('Abilify', 'Aripiprazole', 'Depression, bipolar disorder, schizophrenia'),
            ('Seroquel', 'Quetiapine', 'Bipolar disorder, schizophrenia'),
            ('Risperdal', 'Risperidone', 'Schizophrenia, bipolar disorder'),
            ('Zyprexa', 'Olanzapine', 'Bipolar disorder, schizophrenia'),
            ('Geodon', 'Ziprasidone', 'Bipolar disorder, schizophrenia'),
            ('Latuda', 'Lurasidone', 'Bipolar disorder, schizophrenia'),
            ('Rexulti', 'Brexpiprazole', 'Depression, schizophrenia'),
            ('Vraylar', 'Cariprazine', 'Bipolar disorder, schizophrenia'),
            ('Haldol', 'Haloperidol', 'Schizophrenia, agitation'),
            ('Thorazine', 'Chlorpromazine', 'Schizophrenia'),
            ('Prolixin', 'Fluphenazine', 'Schizophrenia'),
            ('Navane', 'Thiothixene', 'Schizophrenia'),
            ('Mellaril', 'Thioridazine', 'Schizophrenia'),
            ('Stelazine', 'Trifluoperazine', 'Schizophrenia'),
            ('Lithium', 'Lithium', 'Bipolar disorder'),
            ('Lithobid', 'Lithium', 'Bipolar disorder'),
            ('Depakote', 'Divalproex', 'Bipolar disorder, seizures'),
            ('Tegretol', 'Carbamazepine', 'Bipolar disorder, seizures'),
            ('Lamictal', 'Lamotrigine', 'Bipolar disorder, seizures'),
            ('Trileptal', 'Oxcarbazepine', 'Bipolar disorder, seizures'),
            ('Neurontin', 'Gabapentin', 'Neuropathy, seizures'),
            ('Lyrica', 'Pregabalin', 'Neuropathy, fibromyalgia'),

            # Anxiety and sleep medications
            ('Xanax', 'Alprazolam', 'Anxiety, panic disorder'),
            ('Ativan', 'Lorazepam', 'Anxiety, insomnia'),
            ('Valium', 'Diazepam', 'Anxiety, muscle spasms'),
            ('Klonopin', 'Clonazepam', 'Anxiety, seizures'),
            ('Librium', 'Chlordiazepoxide', 'Anxiety'),
            ('Serax', 'Oxazepam', 'Anxiety'),
            ('Tranxene', 'Clorazepate', 'Anxiety'),
            ('Centrax', 'Prazepam', 'Anxiety'),
            ('Dalmane', 'Flurazepam', 'Insomnia'),
            ('Halcion', 'Triazolam', 'Insomnia'),
            ('Restoril', 'Temazepam', 'Insomnia'),
            ('ProSom', 'Estazolam', 'Insomnia'),
            ('Versed', 'Midazolam', 'Sedation'),
            ('Ambien', 'Zolpidem', 'Insomnia'),
            ('Lunesta', 'Eszopiclone', 'Insomnia'),
            ('Sonata', 'Zaleplon', 'Insomnia'),
            ('Rozerem', 'Ramelteon', 'Insomnia'),
            ('Belsomra', 'Suvorexant', 'Insomnia'),
            ('Silenor', 'Doxepin', 'Insomnia'),
            ('Buspar', 'Buspirone', 'Anxiety'),
            ('Vistaril', 'Hydroxyzine', 'Anxiety, itching'),
            ('Atarax', 'Hydroxyzine', 'Anxiety, itching'),

            # Thyroid medications
            ('Synthroid', 'Levothyroxine', 'Hypothyroidism'),
            ('Levoxyl', 'Levothyroxine', 'Hypothyroidism'),
            ('Unithroid', 'Levothyroxine', 'Hypothyroidism'),
            ('Levothroid', 'Levothyroxine', 'Hypothyroidism'),
            ('Tirosint', 'Levothyroxine', 'Hypothyroidism'),
            ('Armour Thyroid', 'Thyroid desiccated', 'Hypothyroidism'),
            ('Nature-Throid', 'Thyroid desiccated', 'Hypothyroidism'),
            ('WP Thyroid', 'Thyroid desiccated', 'Hypothyroidism'),
            ('Cytomel', 'Liothyronine', 'Hypothyroidism'),
            ('Triostat', 'Liothyronine', 'Hypothyroidism'),
            ('Thyrolar', 'Liotrix', 'Hypothyroidism'),
            ('Tapazole', 'Methimazole', 'Hyperthyroidism'),
            ('PTU', 'Propylthiouracil', 'Hyperthyroidism'),

            # Gastrointestinal medications
            ('Nexium', 'Esomeprazole', 'GERD, stomach ulcers'),
            ('Prilosec', 'Omeprazole', 'GERD, stomach ulcers'),
            ('Prevacid', 'Lansoprazole', 'GERD, stomach ulcers'),
            ('Protonix', 'Pantoprazole', 'GERD, stomach ulcers'),
            ('AcipHex', 'Rabeprazole', 'GERD, stomach ulcers'),
            ('Dexilant', 'Dexlansoprazole', 'GERD'),
            ('Zantac', 'Ranitidine', 'Heartburn, ulcers'),
            ('Pepcid', 'Famotidine', 'Heartburn, ulcers'),
            ('Tagamet', 'Cimetidine', 'Heartburn, ulcers'),
            ('Axid', 'Nizatidine', 'Heartburn, ulcers'),
            ('Carafate', 'Sucralfate', 'Stomach ulcers'),
            ('Cytotec', 'Misoprostol', 'Stomach ulcer prevention'),
            ('Reglan', 'Metoclopramide', 'Gastroparesis, nausea'),
            ('Domperidone', 'Domperidone', 'Gastroparesis'),
            ('Bentyl', 'Dicyclomine', 'IBS, stomach spasms'),
            ('Librax', 'Chlordiazepoxide/Clidinium', 'IBS, stomach spasms'),
            ('Donnatal', 'Belladonna/Phenobarbital', 'IBS, stomach spasms'),
            ('Hyoscyamine', 'Hyoscyamine', 'IBS, stomach spasms'),
            ('Levsin', 'Hyoscyamine', 'IBS, stomach spasms'),
            ('Lomotil', 'Diphenoxylate/Atropine', 'Diarrhea'),
            ('Imodium', 'Loperamide', 'Diarrhea'),
            ('Pepto-Bismol', 'Bismuth subsalicylate', 'Diarrhea, upset stomach'),
            ('Colace', 'Docusate', 'Constipation'),
            ('Senokot', 'Senna', 'Constipation'),
            ('Dulcolax', 'Bisacodyl', 'Constipation'),
            ('MiraLAX', 'Polyethylene glycol', 'Constipation'),
            ('Lactulose', 'Lactulose', 'Constipation'),
            ('Metamucil', 'Psyllium', 'Constipation, fiber supplement'),
            ('Citrucel', 'Methylcellulose', 'Constipation'),
            ('FiberCon', 'Polycarbophil', 'Constipation'),
            ('Linzess', 'Linaclotide', 'IBS with constipation'),
            ('Amitiza', 'Lubiprostone', 'Constipation'),
            ('Trulance', 'Plecanatide', 'Constipation'),
            ('Motegrity', 'Prucalopride', 'Constipation'),

            # Respiratory medications
            ('Advair', 'Fluticasone/Salmeterol', 'Asthma, COPD'),
            ('Symbicort', 'Budesonide/Formoterol', 'Asthma, COPD'),
            ('Dulera', 'Mometasone/Formoterol', 'Asthma'),
            ('Breo', 'Fluticasone/Vilanterol', 'Asthma, COPD'),
            ('Trelegy', 'Fluticasone/Umeclidinium/Vilanterol', 'COPD'),
            ('Spiriva', 'Tiotropium', 'COPD'),
            ('Combivent', 'Ipratropium/Albuterol', 'COPD'),
            ('DuoNeb', 'Ipratropium/Albuterol', 'COPD'),
            ('Atrovent', 'Ipratropium', 'COPD'),
            ('ProAir', 'Albuterol', 'Asthma, bronchospasm'),
            ('Ventolin', 'Albuterol', 'Asthma, bronchospasm'),
            ('Xopenex', 'Levalbuterol', 'Asthma, bronchospasm'),
            ('Maxair', 'Pirbuterol', 'Asthma'),
            ('Serevent', 'Salmeterol', 'Asthma, COPD'),
            ('Foradil', 'Formoterol', 'Asthma, COPD'),
            ('Perforomist', 'Formoterol', 'COPD'),
            ('Brovana', 'Arformoterol', 'COPD'),
            ('Striverdi', 'Olodaterol', 'COPD'),
            ('Arcapta', 'Indacaterol', 'COPD'),
            ('Tudorza', 'Aclidinium', 'COPD'),
            ('Seebri', 'Glycopyrrolate', 'COPD'),
            ('Lonhala', 'Glycopyrrolate', 'COPD'),
            ('Yupelri', 'Revefenacin', 'COPD'),
            ('Flovent', 'Fluticasone', 'Asthma'),
            ('Pulmicort', 'Budesonide', 'Asthma'),
            ('Asmanex', 'Mometasone', 'Asthma'),
            ('Qvar', 'Beclomethasone', 'Asthma'),
            ('Alvesco', 'Ciclesonide', 'Asthma'),
            ('Aerospan', 'Flunisolide', 'Asthma'),
            ('Singular', 'Montelukast', 'Asthma, allergies'),
            ('Accolate', 'Zafirlukast', 'Asthma'),
            ('Zyflo', 'Zileuton', 'Asthma'),
            ('Xolair', 'Omalizumab', 'Severe asthma'),
            ('Nucala', 'Mepolizumab', 'Severe asthma'),
            ('Cinqair', 'Reslizumab', 'Severe asthma'),
            ('Fasenra', 'Benralizumab', 'Severe asthma'),
            ('Dupixent', 'Dupilumab', 'Severe asthma'),
            ('Theo-Dur', 'Theophylline', 'Asthma, COPD'),
            ('Uniphyl', 'Theophylline', 'Asthma, COPD'),

            # Allergy medications
            ('Zyrtec', 'Cetirizine', 'Allergies'),
            ('Claritin', 'Loratadine', 'Allergies'),
            ('Allegra', 'Fexofenadine', 'Allergies'),
            ('Xyzal', 'Levocetirizine', 'Allergies'),
            ('Clarinex', 'Desloratadine', 'Allergies'),
            ('Benadryl', 'Diphenhydramine', 'Allergies, sleep aid'),
            ('Chlor-Trimeton', 'Chlorpheniramine', 'Allergies'),
            ('Tavist', 'Clemastine', 'Allergies'),
            ('Dimetane', 'Brompheniramine', 'Allergies'),
            ('Periactin', 'Cyproheptadine', 'Allergies, appetite stimulant'),
            ('Flonase', 'Fluticasone', 'Nasal allergies'),
            ('Nasacort', 'Triamcinolone', 'Nasal allergies'),
            ('Rhinocort', 'Budesonide', 'Nasal allergies'),
            ('Nasonex', 'Mometasone', 'Nasal allergies'),
            ('Omnaris', 'Ciclesonide', 'Nasal allergies'),
            ('Qnasl', 'Beclomethasone', 'Nasal allergies'),
            ('Zetonna', 'Ciclesonide', 'Nasal allergies'),
            ('Dymista', 'Azelastine/Fluticasone', 'Nasal allergies'),
            ('Astelin', 'Azelastine', 'Nasal allergies'),
            ('Astepro', 'Azelastine', 'Nasal allergies'),
            ('Patanase', 'Olopatadine', 'Nasal allergies'),

            # Neurological medications
            ('Aricept', 'Donepezil', 'Alzheimer\'s disease'),
            ('Exelon', 'Rivastigmine', 'Alzheimer\'s disease'),
            ('Razadyne', 'Galantamine', 'Alzheimer\'s disease'),
            ('Namenda', 'Memantine', 'Alzheimer\'s disease'),
            ('Namzaric', 'Donepezil/Memantine', 'Alzheimer\'s disease'),
            ('Sinemet', 'Carbidopa/Levodopa', 'Parkinson\'s disease'),
            ('Stalevo', 'Carbidopa/Levodopa/Entacapone', 'Parkinson\'s disease'),
            ('Rytary', 'Carbidopa/Levodopa', 'Parkinson\'s disease'),
            ('Duopa', 'Carbidopa/Levodopa', 'Parkinson\'s disease'),
            ('Inbrija', 'Levodopa', 'Parkinson\'s disease'),
            ('Mirapex', 'Pramipexole', 'Parkinson\'s disease, restless legs'),
            ('Requip', 'Ropinirole', 'Parkinson\'s disease, restless legs'),
            ('Neupro', 'Rotigotine', 'Parkinson\'s disease'),
            ('Parlodel', 'Bromocriptine', 'Parkinson\'s disease'),
            ('Permax', 'Pergolide', 'Parkinson\'s disease'),
            ('Apokyn', 'Apomorphine', 'Parkinson\'s disease'),
            ('Azilect', 'Rasagiline', 'Parkinson\'s disease'),
            ('Zelapar', 'Selegiline', 'Parkinson\'s disease'),
            ('Eldepryl', 'Selegiline', 'Parkinson\'s disease'),
            ('Comtan', 'Entacapone', 'Parkinson\'s disease'),
            ('Tasmar', 'Tolcapone', 'Parkinson\'s disease'),
            ('Artane', 'Trihexyphenidyl', 'Parkinson\'s disease'),
            ('Cogentin', 'Benztropine', 'Parkinson\'s disease'),
            ('Symmetrel', 'Amantadine', 'Parkinson\'s disease'),
            ('Gocovri', 'Amantadine', 'Parkinson\'s disease'),
            ('Osmolex', 'Amantadine', 'Parkinson\'s disease'),

            # Seizure medications
            ('Dilantin', 'Phenytoin', 'Seizures'),
            ('Tegretol', 'Carbamazepine', 'Seizures, bipolar disorder'),
            ('Depakote', 'Divalproex', 'Seizures, bipolar disorder'),
            ('Lamictal', 'Lamotrigine', 'Seizures, bipolar disorder'),
            ('Keppra', 'Levetiracetam', 'Seizures'),
            ('Trileptal', 'Oxcarbazepine', 'Seizures'),
            ('Topamax', 'Topiramate', 'Seizures, migraine prevention'),
            ('Neurontin', 'Gabapentin', 'Seizures, neuropathy'),
            ('Lyrica', 'Pregabalin', 'Seizures, neuropathy'),
            ('Zonegran', 'Zonisamide', 'Seizures'),
            ('Vimpat', 'Lacosamide', 'Seizures'),
            ('Banzel', 'Rufinamide', 'Seizures'),
            ('Fycompa', 'Perampanel', 'Seizures'),
            ('Aptiom', 'Eslicarbazepine', 'Seizures'),
            ('Briviact', 'Brivaracetam', 'Seizures'),
            ('Onfi', 'Clobazam', 'Seizures'),
            ('Sabril', 'Vigabatrin', 'Seizures'),
            ('Gabitril', 'Tiagabine', 'Seizures'),
            ('Felbamate', 'Felbamate', 'Seizures'),
            ('Phenobarbital', 'Phenobarbital', 'Seizures'),
            ('Primidone', 'Primidone', 'Seizures'),
            ('Ethosuximide', 'Ethosuximide', 'Absence seizures'),
            ('Zarontin', 'Ethosuximide', 'Absence seizures'),
            ('Celontin', 'Methsuximide', 'Absence seizures'),
            ('Peganone', 'Ethotoin', 'Seizures'),
            ('Mesantoin', 'Mephenytoin', 'Seizures'),
            ('Cerebyx', 'Fosphenytoin', 'Seizures'),
            ('Mysoline', 'Primidone', 'Seizures'),

            # Eye medications
            ('Timoptic', 'Timolol', 'Glaucoma'),
            ('Xalatan', 'Latanoprost', 'Glaucoma'),
            ('Lumigan', 'Bimatoprost', 'Glaucoma'),
            ('Travatan', 'Travoprost', 'Glaucoma'),
            ('Zioptan', 'Tafluprost', 'Glaucoma'),
            ('Vyzulta', 'Latanoprostene bunod', 'Glaucoma'),
            ('Rhopressa', 'Netarsudil', 'Glaucoma'),
            ('Rocklatan', 'Netarsudil/Latanoprost', 'Glaucoma'),
            ('Alphagan', 'Brimonidine', 'Glaucoma'),
            ('Iopidine', 'Apraclonidine', 'Glaucoma'),
            ('Trusopt', 'Dorzolamide', 'Glaucoma'),
            ('Azopt', 'Brinzolamide', 'Glaucoma'),
            ('Cosopt', 'Dorzolamide/Timolol', 'Glaucoma'),
            ('Combigan', 'Brimonidine/Timolol', 'Glaucoma'),
            ('Simbrinza', 'Brinzolamide/Brimonidine', 'Glaucoma'),
            ('Diamox', 'Acetazolamide', 'Glaucoma'),
            ('Neptazane', 'Methazolamide', 'Glaucoma'),
            ('Pilocarpine', 'Pilocarpine', 'Glaucoma'),
            ('Isopto Carpine', 'Pilocarpine', 'Glaucoma'),

            # Vitamins and supplements
            ('Vitamin D3', 'Cholecalciferol', 'Bone health, vitamin deficiency'),
            ('Vitamin B12', 'Cyanocobalamin', 'B12 deficiency, neuropathy'),
            ('Folic Acid', 'Folic acid', 'Folate deficiency, anemia'),
            ('Iron', 'Ferrous sulfate', 'Iron deficiency anemia'),
            ('Calcium', 'Calcium carbonate', 'Bone health'),
            ('Magnesium', 'Magnesium oxide', 'Magnesium deficiency'),
            ('Potassium', 'Potassium chloride', 'Potassium deficiency'),
            ('Multivitamin', 'Multivitamin', 'Nutritional supplement'),
            ('Omega-3', 'Fish oil', 'Heart health, inflammation'),
            ('Coenzyme Q10', 'Ubiquinone', 'Heart health, energy'),
            ('Probiotics', 'Lactobacillus', 'Digestive health'),
            ('Glucosamine', 'Glucosamine sulfate', 'Joint health'),
            ('Chondroitin', 'Chondroitin sulfate', 'Joint health'),
            ('Melatonin', 'Melatonin', 'Sleep disorders'),
            ('Biotin', 'Biotin', 'Hair, skin, nail health'),
            ('Vitamin C', 'Ascorbic acid', 'Immune support, antioxidant'),
            ('Vitamin E', 'Tocopherol', 'Antioxidant'),
            ('Zinc', 'Zinc sulfate', 'Immune support, wound healing'),
            ('Selenium', 'Selenium', 'Antioxidant'),
            ('Thiamine', 'Vitamin B1', 'B1 deficiency'),
            ('Riboflavin', 'Vitamin B2', 'B2 deficiency'),
            ('Niacin', 'Vitamin B3', 'Cholesterol, B3 deficiency'),
            ('Pyridoxine', 'Vitamin B6', 'B6 deficiency'),
            ('Pantothenic Acid', 'Vitamin B5', 'B5 deficiency'),

            # Hormones
            ('Premarin', 'Conjugated estrogens', 'Menopause symptoms'),
            ('Estrace', 'Estradiol', 'Menopause symptoms'),
            ('Climara', 'Estradiol', 'Menopause symptoms'),
            ('Vivelle', 'Estradiol', 'Menopause symptoms'),
            ('Provera', 'Medroxyprogesterone', 'Menopause, contraception'),
            ('Prometrium', 'Progesterone', 'Menopause'),
            ('Prempro', 'Estrogen/Progestin', 'Menopause symptoms'),
            ('Femhrt', 'Estrogen/Progestin', 'Menopause symptoms'),
            ('Activella', 'Estrogen/Progestin', 'Menopause symptoms'),
            ('Testosterone', 'Testosterone', 'Low testosterone'),
            ('AndroGel', 'Testosterone', 'Low testosterone'),
            ('Testim', 'Testosterone', 'Low testosterone'),
            ('Axiron', 'Testosterone', 'Low testosterone'),
            ('Fortesta', 'Testosterone', 'Low testosterone'),
            ('Vogelxo', 'Testosterone', 'Low testosterone'),

            # Migraine medications
            ('Imitrex', 'Sumatriptan', 'Migraine headaches'),
            ('Maxalt', 'Rizatriptan', 'Migraine headaches'),
            ('Zomig', 'Zolmitriptan', 'Migraine headaches'),
            ('Amerge', 'Naratriptan', 'Migraine headaches'),
            ('Relpax', 'Eletriptan', 'Migraine headaches'),
            ('Frova', 'Frovatriptan', 'Migraine headaches'),
            ('Axert', 'Almotriptan', 'Migraine headaches'),
            ('Treximet', 'Sumatriptan/Naproxen', 'Migraine headaches'),
            ('DHE', 'Dihydroergotamine', 'Migraine headaches'),
            ('Migranal', 'Dihydroergotamine', 'Migraine headaches'),
            ('Ergomar', 'Ergotamine', 'Migraine headaches'),
            ('Cafergot', 'Ergotamine/Caffeine', 'Migraine headaches'),
            ('Midrin', 'Isometheptene/Dichloralphenazone/Acetaminophen', 'Migraine headaches'),
            ('Fioricet', 'Butalbital/Acetaminophen/Caffeine', 'Tension headaches'),
            ('Fiorinal', 'Butalbital/Aspirin/Caffeine', 'Tension headaches'),
            ('Esgic', 'Butalbital/Acetaminophen/Caffeine', 'Tension headaches'),

            # Additional antibiotics commonly used in elderly care
            ('Amoxicillin', 'Amoxicillin', 'Bacterial infections, UTI'),
            ('Azithromycin', 'Azithromycin', 'Respiratory infections, skin infections'),
            ('Ciprofloxacin', 'Ciprofloxacin', 'UTI, respiratory infections'),
            ('Levofloxacin', 'Levofloxacin', 'Pneumonia, UTI, skin infections'),
            ('Cephalexin', 'Cephalexin', 'Skin infections, UTI'),
            ('Clindamycin', 'Clindamycin', 'Skin infections, dental infections'),
            ('Doxycycline', 'Doxycycline', 'Respiratory infections, skin conditions'),
            ('Trimethoprim-Sulfamethoxazole', 'TMP-SMX', 'UTI, MRSA infections'),
            ('Bactrim', 'Trimethoprim-Sulfamethoxazole', 'UTI, pneumonia'),
            ('Augmentin', 'Amoxicillin-Clavulanate', 'Respiratory infections, UTI'),
            ('Cefdinir', 'Cefdinir', 'Respiratory infections'),
            ('Nitrofurantoin', 'Nitrofurantoin', 'UTI prevention and treatment'),
            ('Macrobid', 'Nitrofurantoin', 'UTI'),
            ('Vancomycin', 'Vancomycin', 'MRSA infections, C. diff'),
            ('Metronidazole', 'Metronidazole', 'C. diff, anaerobic infections'),
            ('Flagyl', 'Metronidazole', 'Bacterial infections, C. diff'),
            ('Erythromycin', 'Erythromycin', 'Respiratory infections'),
            ('Clarithromycin', 'Clarithromycin', 'Respiratory infections'),
            ('Biaxin', 'Clarithromycin', 'Pneumonia, bronchitis'),

            # Antifungal medications
            ('Fluconazole', 'Fluconazole', 'Yeast infections, thrush'),
            ('Diflucan', 'Fluconazole', 'Vaginal yeast infections'),
            ('Nystatin', 'Nystatin', 'Oral thrush, skin yeast infections'),
            ('Ketoconazole', 'Ketoconazole', 'Fungal infections'),
            ('Itraconazole', 'Itraconazole', 'Fungal infections'),
            ('Sporanox', 'Itraconazole', 'Nail fungus, systemic fungal infections'),
            ('Terbinafine', 'Terbinafine', 'Nail fungus, athlete\'s foot'),
            ('Lamisil', 'Terbinafine', 'Fungal nail infections'),

            # Antiviral medications
            ('Acyclovir', 'Acyclovir', 'Herpes, shingles'),
            ('Zovirax', 'Acyclovir', 'Cold sores, shingles'),
            ('Valacyclovir', 'Valacyclovir', 'Herpes, shingles'),
            ('Valtrex', 'Valacyclovir', 'Herpes outbreaks, shingles'),
            ('Famciclovir', 'Famciclovir', 'Herpes, shingles'),
            ('Famvir', 'Famciclovir', 'Herpes zoster, genital herpes'),
            ('Oseltamivir', 'Oseltamivir', 'Influenza A and B'),
            ('Tamiflu', 'Oseltamivir', 'Flu treatment and prevention'),

            # Skin and wound care medications
            ('Mupirocin', 'Mupirocin', 'Bacterial skin infections'),
            ('Bactroban', 'Mupirocin', 'Impetigo, MRSA skin infections'),
            ('Silver Sulfadiazine', 'Silver Sulfadiazine', 'Burn treatment'),
            ('Silvadene', 'Silver Sulfadiazine', 'Burn wound care'),
            ('Bacitracin', 'Bacitracin', 'Minor cuts, wound prevention'),
            ('Neosporin', 'Neomycin/Polymyxin/Bacitracin', 'Minor wound care'),
            ('Hydrocortisone', 'Hydrocortisone', 'Skin inflammation, eczema'),
            ('Triamcinolone', 'Triamcinolone', 'Skin inflammation, allergies'),
            ('Kenalog', 'Triamcinolone', 'Skin conditions, joint injections'),
            ('Betamethasone', 'Betamethasone', 'Severe skin inflammation'),
            ('Clobetasol', 'Clobetasol', 'Severe skin conditions'),
            ('Temovate', 'Clobetasol', 'Psoriasis, severe dermatitis'),
            ('Calamine', 'Calamine', 'Itchy skin, minor irritation'),
            ('Zinc Oxide', 'Zinc Oxide', 'Diaper rash, skin protection'),

            # Additional diabetes medications
            ('Glyburide', 'Glyburide', 'Type 2 diabetes'),
            ('Glimepiride', 'Glimepiride', 'Type 2 diabetes'),
            ('Repaglinide', 'Repaglinide', 'Type 2 diabetes'),
            ('Nateglinide', 'Nateglinide', 'Type 2 diabetes'),
            ('Pioglitazone', 'Pioglitazone', 'Type 2 diabetes'),
            ('Acarbose', 'Acarbose', 'Type 2 diabetes'),
            ('Miglitol', 'Miglitol', 'Type 2 diabetes'),
            ('Saxagliptin', 'Saxagliptin', 'Type 2 diabetes'),
            ('Alogliptin', 'Alogliptin', 'Type 2 diabetes'),
            ('Canagliflozin', 'Canagliflozin', 'Type 2 diabetes'),
            ('Dapagliflozin', 'Dapagliflozin', 'Type 2 diabetes'),
            ('Empagliflozin', 'Empagliflozin', 'Type 2 diabetes'),
            ('Liraglutide', 'Liraglutide', 'Type 2 diabetes'),
            ('Exenatide', 'Exenatide', 'Type 2 diabetes'),
            ('Dulaglutide', 'Dulaglutide', 'Type 2 diabetes'),
            ('Semaglutide', 'Semaglutide', 'Type 2 diabetes'),

            # Additional blood pressure medications
            ('Enalapril', 'Enalapril', 'High blood pressure, heart failure'),
            ('Captopril', 'Captopril', 'High blood pressure, heart failure'),
            ('Ramipril', 'Ramipril', 'High blood pressure, heart failure'),
            ('Quinapril', 'Quinapril', 'High blood pressure'),
            ('Fosinopril', 'Fosinopril', 'High blood pressure'),
            ('Benazepril', 'Benazepril', 'High blood pressure'),
            ('Perindopril', 'Perindopril', 'High blood pressure'),
            ('Trandolapril', 'Trandolapril', 'High blood pressure'),
            ('Valsartan', 'Valsartan', 'High blood pressure'),
            ('Irbesartan', 'Irbesartan', 'High blood pressure'),
            ('Candesartan', 'Candesartan', 'High blood pressure'),
            ('Telmisartan', 'Telmisartan', 'High blood pressure'),
            ('Olmesartan', 'Olmesartan', 'High blood pressure'),
            ('Azilsartan', 'Azilsartan', 'High blood pressure'),

            # Anti-inflammatory and arthritis medications
            ('Prednisone', 'Prednisone', 'Inflammation, autoimmune conditions'),
            ('Prednisolone', 'Prednisolone', 'Inflammation, allergies'),
            ('Methylprednisolone', 'Methylprednisolone', 'Severe inflammation'),
            ('Medrol', 'Methylprednisolone', 'Inflammation, allergies'),
            ('Dexamethasone', 'Dexamethasone', 'Severe inflammation'),
            ('Decadron', 'Dexamethasone', 'Brain swelling, severe allergies'),
            ('Cortisone', 'Cortisone', 'Inflammation, joint pain'),
            ('Hydrocortisone', 'Hydrocortisone', 'Adrenal insufficiency'),
            ('Fludrocortisone', 'Fludrocortisone', 'Adrenal insufficiency'),
            ('Florinef', 'Fludrocortisone', 'Addison\'s disease'),

            # Additional pain medications
            ('Hydrocodone', 'Hydrocodone', 'Moderate to severe pain'),
            ('Vicodin', 'Hydrocodone/Acetaminophen', 'Pain relief'),
            ('Norco', 'Hydrocodone/Acetaminophen', 'Pain relief'),
            ('Lortab', 'Hydrocodone/Acetaminophen', 'Pain relief'),
            ('Oxycodone', 'Oxycodone', 'Moderate to severe pain'),
            ('OxyContin', 'Oxycodone', 'Chronic pain'),
            ('Percocet', 'Oxycodone/Acetaminophen', 'Pain relief'),
            ('Percodan', 'Oxycodone/Aspirin', 'Pain relief'),
            ('Codeine', 'Codeine', 'Mild to moderate pain'),
            ('Tylenol #3', 'Codeine/Acetaminophen', 'Pain relief'),
            ('Morphine', 'Morphine', 'Severe pain'),
            ('MS Contin', 'Morphine', 'Chronic severe pain'),
            ('Fentanyl', 'Fentanyl', 'Severe chronic pain'),
            ('Duragesic', 'Fentanyl', 'Chronic pain patch'),
            ('Buprenorphine', 'Buprenorphine', 'Opioid addiction, pain'),
            ('Suboxone', 'Buprenorphine/Naloxone', 'Opioid addiction'),

            # Muscle relaxants
            ('Cyclobenzaprine', 'Cyclobenzaprine', 'Muscle spasms'),
            ('Flexeril', 'Cyclobenzaprine', 'Muscle spasms'),
            ('Baclofen', 'Baclofen', 'Muscle spasticity'),
            ('Lioresal', 'Baclofen', 'Multiple sclerosis spasticity'),
            ('Tizanidine', 'Tizanidine', 'Muscle spasticity'),
            ('Zanaflex', 'Tizanidine', 'Muscle spasms'),
            ('Carisoprodol', 'Carisoprodol', 'Muscle pain'),
            ('Soma', 'Carisoprodol', 'Acute muscle pain'),
            ('Methocarbamol', 'Methocarbamol', 'Muscle spasms'),
            ('Robaxin', 'Methocarbamol', 'Muscle pain'),
            ('Chlorzoxazone', 'Chlorzoxazone', 'Muscle spasms'),
            ('Paraflex', 'Chlorzoxazone', 'Muscle pain'),
            ('Metaxalone', 'Metaxalone', 'Muscle spasms'),
            ('Skelaxin', 'Metaxalone', 'Muscle pain'),

            # Additional psychiatric medications
            ('Paroxetine', 'Paroxetine', 'Depression, anxiety'),
            ('Paxil', 'Paroxetine', 'Depression, panic disorder'),
            ('Citalopram', 'Citalopram', 'Depression'),
            ('Celexa', 'Citalopram', 'Depression'),
            ('Fluvoxamine', 'Fluvoxamine', 'OCD, depression'),
            ('Luvox', 'Fluvoxamine', 'Obsessive-compulsive disorder'),
            ('Desvenlafaxine', 'Desvenlafaxine', 'Depression'),
            ('Pristiq', 'Desvenlafaxine', 'Major depressive disorder'),
            ('Levomilnacipran', 'Levomilnacipran', 'Depression'),
            ('Fetzima', 'Levomilnacipran', 'Major depressive disorder'),
            ('Vilazodone', 'Vilazodone', 'Depression'),
            ('Viibryd', 'Vilazodone', 'Major depressive disorder'),
            ('Vortioxetine', 'Vortioxetine', 'Depression'),
            ('Trintellix', 'Vortioxetine', 'Major depressive disorder'),

            # Additional antipsychotics
            ('Haloperidol', 'Haloperidol', 'Schizophrenia, agitation'),
            ('Haldol', 'Haloperidol', 'Psychosis, agitation'),
            ('Chlorpromazine', 'Chlorpromazine', 'Schizophrenia'),
            ('Thorazine', 'Chlorpromazine', 'Psychosis, severe behavioral problems'),
            ('Fluphenazine', 'Fluphenazine', 'Schizophrenia'),
            ('Prolixin', 'Fluphenazine', 'Chronic schizophrenia'),
            ('Perphenazine', 'Perphenazine', 'Schizophrenia'),
            ('Trilafon', 'Perphenazine', 'Psychosis'),
            ('Thioridazine', 'Thioridazine', 'Schizophrenia'),
            ('Mellaril', 'Thioridazine', 'Psychosis'),
            ('Thiothixene', 'Thiothixene', 'Schizophrenia'),
            ('Navane', 'Thiothixene', 'Psychotic disorders'),
            ('Paliperidone', 'Paliperidone', 'Schizophrenia'),
            ('Invega', 'Paliperidone', 'Schizoaffective disorder'),
            ('Iloperidone', 'Iloperidone', 'Schizophrenia'),
            ('Fanapt', 'Iloperidone', 'Acute schizophrenia'),
            ('Asenapine', 'Asenapine', 'Bipolar disorder, schizophrenia'),
            ('Saphris', 'Asenapine', 'Bipolar mania'),

            # Mood stabilizers
            ('Lithium Carbonate', 'Lithium', 'Bipolar disorder'),
            ('Lithobid', 'Lithium', 'Manic episodes'),
            ('Valproic Acid', 'Valproic acid', 'Bipolar disorder, seizures'),
            ('Depakene', 'Valproic acid', 'Seizures, bipolar disorder'),
            ('Carbamazepine', 'Carbamazepine', 'Bipolar disorder, seizures'),
            ('Tegretol', 'Carbamazepine', 'Trigeminal neuralgia'),
            ('Oxcarbazepine', 'Oxcarbazepine', 'Bipolar disorder, seizures'),
            ('Trileptal', 'Oxcarbazepine', 'Partial seizures'),
            ('Topiramate', 'Topiramate', 'Seizures, migraine prevention'),
            ('Topamax', 'Topiramate', 'Epilepsy, weight loss'),

            # Additional sleep medications
            ('Eszopiclone', 'Eszopiclone', 'Insomnia'),
            ('Lunesta', 'Eszopiclone', 'Sleep disorders'),
            ('Zaleplon', 'Zaleplon', 'Insomnia'),
            ('Sonata', 'Zaleplon', 'Difficulty falling asleep'),
            ('Ramelteon', 'Ramelteon', 'Insomnia'),
            ('Rozerem', 'Ramelteon', 'Sleep-wake cycle disorders'),
            ('Suvorexant', 'Suvorexant', 'Insomnia'),
            ('Belsomra', 'Suvorexant', 'Sleep maintenance'),
            ('Lemborexant', 'Lemborexant', 'Insomnia'),
            ('Dayvigo', 'Lemborexant', 'Sleep disorders'),
            ('Temazepam', 'Temazepam', 'Insomnia'),
            ('Restoril', 'Temazepam', 'Short-term insomnia'),
            ('Flurazepam', 'Flurazepam', 'Insomnia'),
            ('Dalmane', 'Flurazepam', 'Sleep disorders'),

            # Kidney and urinary medications
            ('Tamsulosin', 'Tamsulosin', 'Enlarged prostate'),
            ('Flomax', 'Tamsulosin', 'Benign prostatic hyperplasia'),
            ('Alfuzosin', 'Alfuzosin', 'Enlarged prostate'),
            ('Uroxatral', 'Alfuzosin', 'BPH symptoms'),
            ('Doxazosin', 'Doxazosin', 'High blood pressure, enlarged prostate'),
            ('Cardura', 'Doxazosin', 'Hypertension, BPH'),
            ('Terazosin', 'Terazosin', 'High blood pressure, enlarged prostate'),
            ('Hytrin', 'Terazosin', 'Hypertension, BPH'),
            ('Silodosin', 'Silodosin', 'Enlarged prostate'),
            ('Rapaflo', 'Silodosin', 'BPH symptoms'),
            ('Dutasteride', 'Dutasteride', 'Enlarged prostate'),
            ('Avodart', 'Dutasteride', 'Benign prostatic hyperplasia'),
            ('Oxybutynin', 'Oxybutynin', 'Overactive bladder'),
            ('Ditropan', 'Oxybutynin', 'Urinary incontinence'),
            ('Tolterodine', 'Tolterodine', 'Overactive bladder'),
            ('Detrol', 'Tolterodine', 'Urinary frequency'),
            ('Solifenacin', 'Solifenacin', 'Overactive bladder'),
            ('Vesicare', 'Solifenacin', 'Urinary incontinence'),
            ('Fesoterodine', 'Fesoterodine', 'Overactive bladder'),
            ('Toviaz', 'Fesoterodine', 'Urinary urgency'),

            # Blood thinners and cardiac medications
            ('Rivaroxaban', 'Rivaroxaban', 'Blood clot prevention'),
            ('Xarelto', 'Rivaroxaban', 'Atrial fibrillation, DVT'),
            ('Apixaban', 'Apixaban', 'Blood clot prevention'),
            ('Eliquis', 'Apixaban', 'Stroke prevention'),
            ('Dabigatran', 'Dabigatran', 'Blood clot prevention'),
            ('Pradaxa', 'Dabigatran', 'Atrial fibrillation'),
            ('Edoxaban', 'Edoxaban', 'Blood clot prevention'),
            ('Savaysa', 'Edoxaban', 'DVT, pulmonary embolism'),
            ('Enoxaparin', 'Enoxaparin', 'Blood clot prevention'),
            ('Lovenox', 'Enoxaparin', 'DVT prevention'),
            ('Heparin', 'Heparin', 'Blood clot treatment'),
            ('Fondaparinux', 'Fondaparinux', 'Blood clot prevention'),
            ('Arixtra', 'Fondaparinux', 'DVT prevention'),

            # Additional heart medications
            ('Diltiazem', 'Diltiazem', 'High blood pressure, angina'),
            ('Cardizem', 'Diltiazem', 'Hypertension, atrial fibrillation'),
            ('Verapamil', 'Verapamil', 'High blood pressure, angina'),
            ('Calan', 'Verapamil', 'Hypertension, arrhythmias'),
            ('Nifedipine', 'Nifedipine', 'High blood pressure'),
            ('Procardia', 'Nifedipine', 'Hypertension, angina'),
            ('Felodipine', 'Felodipine', 'High blood pressure'),
            ('Plendil', 'Felodipine', 'Hypertension'),
            ('Isradipine', 'Isradipine', 'High blood pressure'),
            ('DynaCirc', 'Isradipine', 'Hypertension'),
            ('Nicardipine', 'Nicardipine', 'High blood pressure'),
            ('Cardene', 'Nicardipine', 'Hypertension'),

            # Anti-seizure medications
            ('Phenobarbital', 'Phenobarbital', 'Seizures, sedation'),
            ('Luminal', 'Phenobarbital', 'Epilepsy'),
            ('Primidone', 'Primidone', 'Seizures'),
            ('Mysoline', 'Primidone', 'Essential tremor'),
            ('Ethosuximide', 'Ethosuximide', 'Absence seizures'),
            ('Zarontin', 'Ethosuximide', 'Petit mal seizures'),
            ('Valproate', 'Valproate', 'Seizures, bipolar disorder'),
            ('Depacon', 'Valproate', 'Complex partial seizures'),
            ('Levetiracetam', 'Levetiracetam', 'Seizures'),
            ('Keppra', 'Levetiracetam', 'Partial seizures'),
            ('Zonisamide', 'Zonisamide', 'Seizures'),
            ('Zonegran', 'Zonisamide', 'Partial seizures'),
            ('Lacosamide', 'Lacosamide', 'Seizures'),
            ('Vimpat', 'Lacosamide', 'Partial-onset seizures'),

            # Additional eye medications
            ('Brimonidine', 'Brimonidine', 'Glaucoma'),
            ('Alphagan', 'Brimonidine', 'Elevated eye pressure'),
            ('Dorzolamide', 'Dorzolamide', 'Glaucoma'),
            ('Trusopt', 'Dorzolamide', 'Elevated eye pressure'),
            ('Brinzolamide', 'Brinzolamide', 'Glaucoma'),
            ('Azopt', 'Brinzolamide', 'Elevated eye pressure'),
            ('Bimatoprost', 'Bimatoprost', 'Glaucoma'),
            ('Lumigan', 'Bimatoprost', 'Elevated eye pressure'),
            ('Travoprost', 'Travoprost', 'Glaucoma'),
            ('Travatan', 'Travoprost', 'Elevated eye pressure'),
            ('Tafluprost', 'Tafluprost', 'Glaucoma'),
            ('Zioptan', 'Tafluprost', 'Elevated eye pressure'),

            # Osteoporosis medications
            ('Risedronate', 'Risedronate', 'Osteoporosis'),
            ('Actonel', 'Risedronate', 'Bone loss prevention'),
            ('Ibandronate', 'Ibandronate', 'Osteoporosis'),
            ('Boniva', 'Ibandronate', 'Postmenopausal osteoporosis'),
            ('Zoledronic acid', 'Zoledronic acid', 'Osteoporosis'),
            ('Reclast', 'Zoledronic acid', 'Bone loss prevention'),
            ('Denosumab', 'Denosumab', 'Osteoporosis'),
            ('Prolia', 'Denosumab', 'Bone loss in women'),
            ('Teriparatide', 'Teriparatide', 'Osteoporosis'),
            ('Forteo', 'Teriparatide', 'Severe osteoporosis'),
            ('Abaloparatide', 'Abaloparatide', 'Osteoporosis'),
            ('Tymlos', 'Abaloparatide', 'Postmenopausal osteoporosis'),

            # Hormone replacement therapy
            ('Estradiol', 'Estradiol', 'Menopause symptoms'),
            ('Estrace', 'Estradiol', 'Hormone replacement'),
            ('Premarin', 'Conjugated estrogens', 'Menopause, osteoporosis'),
            ('Prempro', 'Estrogen/Progestin', 'Menopause symptoms'),
            ('Climara', 'Estradiol', 'Menopause (patch)'),
            ('Vivelle', 'Estradiol', 'Hormone replacement (patch)'),
            ('Progesterone', 'Progesterone', 'Hormone replacement'),
            ('Prometrium', 'Progesterone', 'Menopause, fertility'),
            ('Testosterone gel', 'Testosterone', 'Low testosterone'),
            ('AndroGel', 'Testosterone', 'Hypogonadism'),

            # Memory and cognitive medications
            ('Rivastigmine', 'Rivastigmine', 'Alzheimer\'s, dementia'),
            ('Exelon', 'Rivastigmine', 'Mild to moderate dementia'),
            ('Galantamine', 'Galantamine', 'Alzheimer\'s disease'),
            ('Razadyne', 'Galantamine', 'Mild to moderate dementia'),
            ('Memantine', 'Memantine', 'Moderate to severe Alzheimer\'s'),
            ('Namenda', 'Memantine', 'Alzheimer\'s disease'),
            ('Modafinil', 'Modafinil', 'Narcolepsy, fatigue'),
            ('Provigil', 'Modafinil', 'Sleep disorders'),
            ('Armodafinil', 'Armodafinil', 'Narcolepsy'),
            ('Nuvigil', 'Armodafinil', 'Shift work sleep disorder'),

            # Additional respiratory medications
            ('Theophylline', 'Theophylline', 'Asthma, COPD'),
            ('Theo-Dur', 'Theophylline', 'Chronic bronchitis'),
            ('Aminophylline', 'Aminophylline', 'Asthma, COPD'),
            ('Ipratropium', 'Ipratropium', 'COPD, asthma'),
            ('Atrovent', 'Ipratropium', 'Bronchospasm'),
            ('Tiotropium', 'Tiotropium', 'COPD'),
            ('Spiriva', 'Tiotropium', 'Chronic bronchitis'),
            ('Aclidinium', 'Aclidinium', 'COPD'),
            ('Tudorza', 'Aclidinium', 'Chronic bronchitis'),
            ('Glycopyrrolate', 'Glycopyrrolate', 'COPD'),
            ('Seebri', 'Glycopyrrolate', 'Chronic bronchitis'),
            ('Umeclidinium', 'Umeclidinium', 'COPD'),
            ('Incruse', 'Umeclidinium', 'Chronic bronchitis'),

            # Nausea and digestive medications
            ('Ondansetron', 'Ondansetron', 'Nausea, vomiting'),
            ('Zofran', 'Ondansetron', 'Chemotherapy nausea'),
            ('Prochlorperazine', 'Prochlorperazine', 'Nausea, vomiting'),
            ('Compazine', 'Prochlorperazine', 'Severe nausea'),
            ('Promethazine', 'Promethazine', 'Nausea, allergies'),
            ('Phenergan', 'Promethazine', 'Motion sickness'),
            ('Meclizine', 'Meclizine', 'Motion sickness, vertigo'),
            ('Antivert', 'Meclizine', 'Dizziness'),
            ('Scopolamine', 'Scopolamine', 'Motion sickness'),
            ('Transderm Scop', 'Scopolamine', 'Motion sickness (patch)'),
            ('Simethicone', 'Simethicone', 'Gas, bloating'),
            ('Gas-X', 'Simethicone', 'Intestinal gas'),
            ('Famotidine', 'Famotidine', 'Heartburn, GERD'),
            ('Pepcid', 'Famotidine', 'Acid indigestion'),

            # Additional diuretics
            ('Chlorthalidone', 'Chlorthalidone', 'High blood pressure'),
            ('Thalitone', 'Chlorthalidone', 'Hypertension, edema'),
            ('Indapamide', 'Indapamide', 'High blood pressure'),
            ('Lozol', 'Indapamide', 'Hypertension'),
            ('Metolazone', 'Metolazone', 'Fluid retention'),
            ('Zaroxolyn', 'Metolazone', 'Edema, hypertension'),
            ('Amiloride', 'Amiloride', 'Fluid retention'),
            ('Midamor', 'Amiloride', 'Hypertension'),
            ('Triamterene', 'Triamterene', 'Fluid retention'),
            ('Dyrenium', 'Triamterene', 'Edema'),
            ('Bumetanide', 'Bumetanide', 'Fluid retention'),
            ('Bumex', 'Bumetanide', 'Heart failure edema'),
            ('Torsemide', 'Torsemide', 'Fluid retention'),
            ('Demadex', 'Torsemide', 'Heart failure, hypertension'),

            # Blood sugar monitoring and related medications
            ('Glucagon', 'Glucagon', 'Severe hypoglycemia'),
            ('GlucaGen', 'Glucagon', 'Emergency low blood sugar'),
            ('Glucose tablets', 'Glucose', 'Mild hypoglycemia'),
            ('Alpha-lipoic acid', 'Alpha-lipoic acid', 'Diabetic neuropathy'),
            ('Chromium', 'Chromium', 'Blood sugar support'),

            # Additional vitamins and supplements
            ('Vitamin B6', 'Pyridoxine', 'B6 deficiency, neuropathy'),
            ('Vitamin B1', 'Thiamine', 'B1 deficiency, neuropathy'),
            ('Vitamin B2', 'Riboflavin', 'B2 deficiency'),
            ('Vitamin B3', 'Niacin', 'Cholesterol, B3 deficiency'),
            ('Vitamin B5', 'Pantothenic acid', 'B5 deficiency'),
            ('Vitamin K', 'Phytonadione', 'Blood clotting, bone health'),
            ('Vitamin A', 'Retinol', 'Vision, immune function'),
            ('Beta-carotene', 'Beta-carotene', 'Antioxidant, vitamin A'),
            ('Lutein', 'Lutein', 'Eye health, macular degeneration'),
            ('Lycopene', 'Lycopene', 'Antioxidant, prostate health'),
            ('Resveratrol', 'Resveratrol', 'Antioxidant, heart health'),
            ('Turmeric', 'Curcumin', 'Anti-inflammatory'),
            ('Ginkgo biloba', 'Ginkgo', 'Memory, circulation'),
            ('Ginseng', 'Panax ginseng', 'Energy, immune support'),
            ('Echinacea', 'Echinacea', 'Immune support'),
            ('Garlic', 'Allicin', 'Heart health, cholesterol'),
            ('Saw palmetto', 'Saw palmetto', 'Prostate health'),

            # Antacids and digestive aids
            ('Aluminum hydroxide', 'Aluminum hydroxide', 'Heartburn, acid indigestion'),
            ('Maalox', 'Aluminum/Magnesium hydroxide', 'Heartburn'),
            ('Mylanta', 'Aluminum/Magnesium/Simethicone', 'Heartburn, gas'),
            ('Rolaids', 'Calcium carbonate/Magnesium', 'Heartburn'),
            ('Tums', 'Calcium carbonate', 'Heartburn, calcium supplement'),
            ('Gaviscon', 'Aluminum/Magnesium/Alginate', 'GERD, heartburn'),
            ('Milk of magnesia', 'Magnesium hydroxide', 'Constipation, heartburn'),
            ('Psyllium husk', 'Psyllium', 'Constipation, IBS'),
            ('Benefiber', 'Wheat dextrin', 'Fiber supplement'),
            ('Miralax', 'Polyethylene glycol', 'Constipation'),

            # Topical pain relievers
            ('Capsaicin', 'Capsaicin', 'Arthritis pain, neuropathy'),
            ('Zostrix', 'Capsaicin', 'Shingles pain'),
            ('Methyl salicylate', 'Methyl salicylate', 'Muscle pain'),
            ('Bengay', 'Methyl salicylate/Menthol', 'Muscle soreness'),
            ('Icy Hot', 'Methyl salicylate/Menthol', 'Muscle pain'),
            ('Aspercreme', 'Trolamine salicylate', 'Arthritis pain'),
            ('Lidocaine', 'Lidocaine', 'Local pain relief'),
            ('Lidoderm', 'Lidocaine', 'Postherpetic neuralgia'),
            ('Diclofenac gel', 'Diclofenac', 'Arthritis pain'),
            ('Voltaren gel', 'Diclofenac', 'Osteoarthritis'),

            # Emergency and rescue medications
            ('Epinephrine', 'Epinephrine', 'Severe allergic reactions'),
            ('EpiPen', 'Epinephrine', 'Anaphylaxis'),
            ('Albuterol inhaler', 'Albuterol', 'Asthma attacks'),
            ('ProAir HFA', 'Albuterol', 'Bronchospasm'),
            ('Nitroglycerin', 'Nitroglycerin', 'Chest pain, angina'),
            ('Nitrostat', 'Nitroglycerin', 'Acute angina'),
            ('Glucose gel', 'Glucose', 'Hypoglycemia'),
            ('Naloxone', 'Naloxone', 'Opioid overdose'),
            ('Narcan', 'Naloxone', 'Opioid reversal'),

            # Combination medications commonly used
            ('Lisinopril/HCTZ', 'Lisinopril/Hydrochlorothiazide', 'Hypertension'),
            ('Zestoretic', 'Lisinopril/HCTZ', 'High blood pressure'),
            ('Losartan/HCTZ', 'Losartan/Hydrochlorothiazide', 'Hypertension'),
            ('Hyzaar', 'Losartan/HCTZ', 'High blood pressure'),
            ('Valsartan/HCTZ', 'Valsartan/Hydrochlorothiazide', 'Hypertension'),
            ('Diovan HCT', 'Valsartan/HCTZ', 'High blood pressure'),
            ('Amlodipine/Benazepril', 'Amlodipine/Benazepril', 'Hypertension'),
            ('Lotrel', 'Amlodipine/Benazepril', 'High blood pressure'),
            ('Amlodipine/Olmesartan', 'Amlodipine/Olmesartan', 'Hypertension'),
            ('Azor', 'Amlodipine/Olmesartan', 'High blood pressure'),
            ('Amlodipine/Valsartan', 'Amlodipine/Valsartan', 'Hypertension'),
            ('Exforge', 'Amlodipine/Valsartan', 'High blood pressure'),

            # Miscellaneous medications for elderly care
            ('Polyethylene glycol', 'PEG 3350', 'Constipation'),
            ('Docusate sodium', 'Docusate', 'Constipation'),
            ('Colace', 'Docusate', 'Stool softener'),
            ('Senna', 'Sennosides', 'Constipation'),
            ('Ex-Lax', 'Senna', 'Laxative'),
            ('Bisacodyl', 'Bisacodyl', 'Constipation'),
            ('Dulcolax', 'Bisacodyl', 'Laxative'),
            ('Magnesium citrate', 'Magnesium citrate', 'Constipation'),
            ('Fleet enema', 'Sodium phosphate', 'Constipation'),
            ('Glycerin suppository', 'Glycerin', 'Constipation'),

            # Wound care and healing
            ('Hydrogel', 'Hydrogel', 'Wound healing'),
            ('Duoderm', 'Hydrocolloid', 'Wound care'),
            ('Tegaderm', 'Transparent film', 'Wound protection'),
            ('Medihoney', 'Medical honey', 'Wound healing'),
            ('Santyl', 'Collagenase', 'Wound debridement'),
            ('Regranex', 'Becaplermin', 'Diabetic ulcers'),

            # Additional specialized medications
            ('Donepezil/Memantine', 'Donepezil/Memantine', 'Alzheimer\'s disease'),
            ('Namzaric', 'Donepezil/Memantine', 'Moderate to severe dementia'),
            ('Carbidopa/Levodopa', 'Carbidopa/Levodopa', 'Parkinson\'s disease'),
            ('Sinemet CR', 'Carbidopa/Levodopa', 'Parkinson\'s (extended release)'),
            ('Pramipexole', 'Pramipexole', 'Parkinson\'s, restless legs'),
            ('Mirapex ER', 'Pramipexole', 'Parkinson\'s (extended release)'),
            ('Ropinirole', 'Ropinirole', 'Parkinson\'s, restless legs'),
            ('Requip XL', 'Ropinirole', 'Parkinson\'s (extended release)'),

            # Specialized elderly care medications
            ('Memantine ER', 'Memantine', 'Alzheimer\'s (extended release)'),
            ('Namenda XR', 'Memantine ER', 'Moderate to severe dementia'),
            ('Rivastigmine patch', 'Rivastigmine', 'Dementia (transdermal)'),
            ('Exelon patch', 'Rivastigmine', 'Alzheimer\'s/Parkinson\'s dementia'),
            ('Galantamine ER', 'Galantamine', 'Alzheimer\'s (extended release)'),
            ('Razadyne ER', 'Galantamine ER', 'Mild to moderate dementia'),

            # End of expanded medication list
        ]
        
        c.executemany('INSERT INTO medications (brand_name, generic_name, common_uses) VALUES (?, ?, ?)', elderly_meds)
        conn.commit()

    conn.close()

init_medications()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///afh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'documents'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB file size limit
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')


# Initialize encryption
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Generate a key for development - in production, set ENCRYPTION_KEY in secrets
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print("Warning: Using generated encryption key. Set ENCRYPTION_KEY in secrets for production.")
cipher = Fernet(ENCRYPTION_KEY.encode())

from models import db, Resident, FoodIntake, LiquidIntake, BowelMovement, UrineOutput, Vitals, EncryptedText

db.init_app(app)
mail = Mail(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# CSRF Protection
csrf = CSRFProtect(app)

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'caregiver'

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    _notes = db.Column(EncryptedText)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    form = db.Column(db.String(50))
    _common_uses = db.Column(EncryptedText)

    @hybrid_property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        self._notes = value

    @hybrid_property
    def common_uses(self):
        return self._common_uses

    @common_uses.setter
    def common_uses(self, value):
        self._common_uses = value

class MedicationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    administered = db.Column(db.Boolean, default=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    _filename = db.Column(EncryptedText, nullable=False)
    _name = db.Column(EncryptedText, nullable=False)
    upload_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date)

    @hybrid_property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class MedicationCatalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    default_dosage = db.Column(db.String(50))
    default_frequency = db.Column(db.String(50))
    _default_notes = db.Column(EncryptedText)
    form = db.Column(db.String(50))
    _common_uses = db.Column(EncryptedText)

    @hybrid_property
    def default_notes(self):
        return self._default_notes

    @default_notes.setter
    def default_notes(self, value):
        self._default_notes = value

    @hybrid_property
    def common_uses(self):
        return self._common_uses

    @common_uses.setter
    def common_uses(self, value):
        self._common_uses = value

# WTForms for CSRF-protected forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('caregiver', 'Caregiver')], validators=[DataRequired()])
    submit = SubmitField('Save User')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[Length(min=8, message="Password must be at least 8 characters long")])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('caregiver', 'Caregiver')], validators=[DataRequired()])
    submit = SubmitField('Save User')

class AddResidentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    medical_info = TextAreaField('Medical Info')
    emergency_contact = StringField('Emergency Contact', validators=[Length(max=100)])
    submit = SubmitField('Save Resident')

class DailyLogWizardForm(FlaskForm):
    step = HiddenField('Step', default='1')
    meal_type = HiddenField('Meal Type', default='breakfast')
    # Step 1: Vitals (Breakfast only)
    systolic = IntegerField('Systolic Blood Pressure', validators=[DataRequired()], render_kw={'placeholder': 'e.g., 120'})
    diastolic = IntegerField('Diastolic Blood Pressure', validators=[DataRequired()], render_kw={'placeholder': 'e.g., 80'})
    pulse = IntegerField('Pulse', validators=[DataRequired()], render_kw={'placeholder': 'e.g., 70'})
    # Step 2: Food Intake
    intake_level = SelectField('Food Intake', choices=[
        ('25%', '25%'), ('50%', '50%'), ('75%', '75%'), ('100%', '100%'), ('Ensure', 'Ensure'), ('Other', 'Other')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes (for Other)', render_kw={'rows': 4})
    # Step 3: Liquid Intake
    liquid_intake = SelectField('Liquid Intake', choices=[
        ('Yes', 'Yes'), ('No', 'No'), ('Partial', 'Partial')
    ], validators=[DataRequired()])
    # Step 4: Bowel Movement
    size = SelectField('Size', choices=[
        ('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')
    ], validators=[DataRequired()])
    consistency = SelectField('Consistency', choices=[
        ('Soft', 'Soft'), ('Medium', 'Medium'), ('Hard', 'Hard')
    ], validators=[DataRequired()])
    # Step 5: Urine Output
    urine_output = SelectField('Urine Output', choices=[
        ('Yes', 'Yes'), ('No', 'No')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit')
    skip = SubmitField('Skip')

class MedicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    dosage = StringField('Dosage', validators=[Length(max=50)])
    frequency = StringField('Frequency', validators=[Length(max=50)])
    notes = TextAreaField('Notes')
    form = StringField('Form', validators=[Length(max=50)])
    common_uses = TextAreaField('Common Uses')
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date')
    submit = SubmitField('Save Medication')

class MedicationLogForm(FlaskForm):
    medication_id = SelectField('Medication', coerce=int, validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    submit = SubmitField('Log Dose')

class DocumentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    file = FileField('File (PDF or Image)', validators=[DataRequired()])
    expiration_date = DateField('Expiration Date')
    submit = SubmitField('Upload Document')

class ReportForm(FlaskForm):
    start_date = DateField('Start Date', default=date.today() - timedelta(days=7))
    end_date = DateField('End Date', default=date.today)
    export_pdf = SubmitField('Export to PDF')

# Input validation and sanitization
def sanitize_input(text):
    if text:
        text = re.sub(r'<[^>]+>', '', text).strip()
    return text

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, ""

# Send email notification
def send_alert_email(subject, body):
    try:
        msg = Message(subject, recipients=[app.config['MAIL_DEFAULT_SENDER']])
        msg.body = body
        mail.send(msg)
    except Exception as e:
        flash(f'Failed to send email: {str(e)}')

# Context processor for current year
@app.context_processor
def utility_processor():
    def get_current_year():
        return datetime.now().year
    return dict(current_year=get_current_year)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = sanitize_input(form.username.data)
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            audit_log = AuditLog(user_id=user.id, action=f"User {username} logged in")
            db.session.add(audit_log)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    audit_log = AuditLog(user_id=current_user.id, action=f"User {current_user.username} logged out")
    db.session.add(audit_log)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    residents = Resident.query.all()
    total_residents = len(residents)
    alerts = []
    today = date.today()
    # Chart data for meal trends (last 7 days)
    start_date = today - timedelta(days=7)
    end_date = today
    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    meal_counts = {d.isoformat(): {'breakfast': 0, 'lunch': 0, 'dinner': 0} for d in date_range}
    for resident in residents:
        food_intakes = FoodIntake.query.filter_by(resident_id=resident.id).filter(FoodIntake.date.between(start_date, end_date)).all()
        meal_types = ['breakfast', 'lunch', 'dinner']
        logged_meals = [food.meal_type for food in food_intakes]
        for meal in meal_types:
            if meal not in logged_meals:
                alerts.append(f"Missing {meal} log for {resident.name}")
        for food in food_intakes:
            date_str = food.date.isoformat()
            if date_str in meal_counts:
                meal_counts[date_str][food.meal_type] += 1
        documents = Document.query.filter_by(resident_id=resident.id).all()
        for doc in documents:
            if doc.expiration_date and doc.expiration_date < today:
                alerts.append(f"Expired document: {doc.name} for {resident.name}")
                send_alert_email("Expired Document Alert", f"Document {doc.name} for {resident.name} expired on {doc.expiration_date}")
        medications = Medication.query.filter_by(resident_id=resident.id).all()
        for med in medications:
            if med.frequency == 'Daily' and (not med.end_date or med.end_date >= today):
                logs = MedicationLog.query.filter_by(medication_id=med.id, date=today).count()
                if logs == 0:
                    alerts.append(f"Missing dose for {med.name} for {resident.name}")
                    send_alert_email("Missing Medication Alert", f"Missing dose for {med.name} for {resident.name} on {today}")
    chart_labels = [d.isoformat() for d in date_range]
    chart_data = {
        'breakfast': [meal_counts[d]['breakfast'] for d in chart_labels],
        'lunch': [meal_counts[d]['lunch'] for d in chart_labels],
        'dinner': [meal_counts[d]['dinner'] for d in chart_labels]
    }
    return render_template('home.html', residents=residents, total_residents=total_residents, alerts=alerts, chart_labels=chart_labels, chart_data=chart_data)

@app.route('/api/medication-suggestions', methods=['GET'])
@login_required
def medication_suggestions():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    query = request.args.get('term', '')
    if not query:
        return jsonify([])
    suggestions = MedicationCatalog.query.filter(
        (MedicationCatalog.name.ilike(f'%{query}%')) |
        (MedicationCatalog._common_uses.ilike(f'%{cipher.encrypt(query.encode()).decode()}%'))
    ).order_by(MedicationCatalog.name).limit(20).all()
    return jsonify([{
        'id': med.id,
        'name': med.name,
        'dosage': med.default_dosage or '',
        'frequency': med.default_frequency or '',
        'notes': med.default_notes or '',
        'form': med.form or '',
        'common_uses': med.common_uses or ''
    } for med in suggestions])

@app.route('/audit_logs')
@login_required
def audit_logs():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('audit_logs.html', logs=logs)

@app.route('/users', methods=['GET'])
@login_required
def users():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    form = AddUserForm()
    if form.validate_on_submit():
        username = sanitize_input(form.username.data)
        password = form.password.data
        role = form.role.data
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message)
            return render_template('add_user.html', title='Add User', form=form)
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('add_user.html', title='Add User', form=form)
        if role not in ['admin', 'caregiver']:
            flash('Invalid role')
            return render_template('add_user.html', title='Add User', form=form)
        new_user = User(username=username, password_hash=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        audit_log = AuditLog(user_id=current_user.id, action=f"Added user {username}")
        db.session.add(audit_log)
        db.session.commit()
        flash('User added successfully.')
        return redirect(url_for('users'))
    return render_template('add_user.html', title='Add User', form=form)

@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    if form.validate_on_submit():
        username = sanitize_input(form.username.data)
        password = form.password.data
        role = form.role.data
        if User.query.filter_by(username=username).first() and username != user.username:
            flash('Username already exists')
            return render_template('add_user.html', title='Edit User', form=form, user=user)
        if role not in ['admin', 'caregiver']:
            flash('Invalid role')
            return render_template('add_user.html', title='Edit User', form=form, user=user)
        user.username = username
        if password:
            is_valid, message = validate_password(password)
            if not is_valid:
                flash(message)
                return render_template('add_user.html', title='Edit User', form=form, user=user)
            user.password_hash = generate_password_hash(password)
        user.role = role
        db.session.commit()
        audit_log = AuditLog(user_id=current_user.id, action=f"Edited user {username}")
        db.session.add(audit_log)
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('users'))
    form.username.data = user.username
    form.role.data = user.role
    return render_template('add_user.html', title='Edit User', form=form, user=user)

@app.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete your own account')
        return redirect(url_for('users'))
    username = user.username
    db.session.delete(user)
    db.session.commit()
    audit_log = AuditLog(user_id=current_user.id, action=f"Deleted user {username}")
    db.session.add(audit_log)
    db.session.commit()
    flash('User deleted successfully.')
    return redirect(url_for('users'))

@app.route('/resident/add', methods=['GET', 'POST'])
@login_required
def add_resident():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    form = AddResidentForm()
    if form.validate_on_submit():
        name = sanitize_input(form.name.data)
        dob = form.dob.data
        medical_info = sanitize_input(form.medical_info.data)
        emergency_contact = sanitize_input(form.emergency_contact.data)
        if not name:
            flash('Name is required')
            return render_template('add_resident.html', title='Add Resident', form=form)
        new_resident = Resident(name=name, dob=dob, medical_info=medical_info, emergency_contact=emergency_contact)
        db.session.add(new_resident)
        db.session.commit()
        audit_log = AuditLog(user_id=current_user.id, action=f"Added resident {name}")
        db.session.add(audit_log)
        db.session.commit()
        flash('Resident added successfully.')
        return redirect(url_for('home'))
    return render_template('add_resident.html', title='Add Resident', form=form)

@app.route('/resident/<int:resident_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resident(resident_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    resident = Resident.query.get_or_404(resident_id)
    form = AddResidentForm()
    if form.validate_on_submit():
        name = sanitize_input(form.name.data)
        dob = form.dob.data
        medical_info = sanitize_input(form.medical_info.data)
        emergency_contact = sanitize_input(form.emergency_contact.data)
        if not name:
            flash('Name is required')
            return render_template('add_resident.html', title='Edit Resident', form=form, resident=resident)
        resident.name = name
        resident.dob = dob
        resident.medical_info = medical_info
        resident.emergency_contact = emergency_contact
        db.session.commit()
        audit_log = AuditLog(user_id=current_user.id, action=f"Edited resident {name}")
        db.session.add(audit_log)
        db.session.commit()
        flash('Resident updated successfully.')
        return redirect(url_for('resident_profile', resident_id=resident_id))
    form.name.data = resident.name
    form.dob.data = resident.dob
    form.medical_info.data = resident.medical_info
    form.emergency_contact.data = resident.emergency_contact
    return render_template('add_resident.html', title='Edit Resident', form=form, resident=resident)

@app.route('/resident/<int:resident_id>/delete', methods=['POST'])
@login_required
def delete_resident(resident_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    resident = Resident.query.get_or_404(resident_id)
    name = resident.name
    db.session.delete(resident)
    db.session.commit()
    audit_log = AuditLog(user_id=current_user.id, action=f"Deleted resident {name}")
    db.session.add(audit_log)
    db.session.commit()
    flash('Resident deleted successfully.')
    return redirect(url_for('home'))

@app.route('/resident/<int:resident_id>')
@login_required
def resident_profile(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    return render_template('resident_profile.html', resident=resident)
@app.route('/search_medications')
def search_medications():
    query = request.args.get('q', '')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        SELECT brand_name, generic_name FROM medications
        WHERE brand_name LIKE ? OR generic_name LIKE ?
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%'))
    results = c.fetchall()
    conn.close()

    return jsonify([
        {'label': f'{brand} ({generic})', 'brand_name': brand, 'generic_name': generic}
        for brand, generic in results
    ])


@app.route('/resident/<int:resident_id>/daily-log-wizard', methods=['GET', 'POST'])
@login_required
def daily_log_wizard(resident_id):
    if current_user.role not in ['admin', 'caregiver']:
        flash('Access denied')
        return redirect(url_for('home'))

    resident = Resident.query.get_or_404(resident_id)
    form = DailyLogWizardForm()
    today = date.today()

    # Initialize session data
    if 'daily_log_wizard' not in session:
        session['daily_log_wizard'] = {
            'breakfast': {'vitals': {}, 'food': {}, 'liquid': {}, 'bowel': {}, 'urine': {}},
            'lunch': {'food': {}, 'liquid': {}, 'bowel': {}, 'urine': {}},
            'dinner': {'food': {}, 'liquid': {}, 'bowel': {}, 'urine': {}}
        }

    # Determine current step and meal
    current_step = int(form.step.data or '1')
    current_meal = form.meal_type.data or 'breakfast'
    steps = [
        {'id': 1, 'name': 'Vitals', 'meal': 'breakfast'},
        {'id': 2, 'name': 'Food Intake', 'meal': 'breakfast'},
        {'id': 3, 'name': 'Liquid Intake', 'meal': 'breakfast'},
        {'id': 4, 'name': 'Bowel Movement', 'meal': 'breakfast'},
        {'id': 5, 'name': 'Urine Output', 'meal': 'breakfast'},
        {'id': 2, 'name': 'Food Intake', 'meal': 'lunch'},
        {'id': 3, 'name': 'Liquid Intake', 'meal': 'lunch'},
        {'id': 4, 'name': 'Bowel Movement', 'meal': 'lunch'},
        {'id': 5, 'name': 'Urine Output', 'meal': 'lunch'},
        {'id': 2, 'name': 'Food Intake', 'meal': 'dinner'},
        {'id': 3, 'name': 'Liquid Intake', 'meal': 'dinner'},
        {'id': 4, 'name': 'Bowel Movement', 'meal': 'dinner'},
        {'id': 5, 'name': 'Urine Output', 'meal': 'dinner'}
    ]
    current_step_index = next(i for i, s in enumerate(steps) if s['id'] == current_step and s['meal'] == current_meal)

    if request.method == 'POST':
        if form.validate_on_submit():
            # Handle Skip
            if form.skip.data:
                # Move to next step without saving data
                next_step_index = min(current_step_index + 1, len(steps) - 1)
                next_step = steps[next_step_index]
                form.step.data = str(next_step['id'])
                form.meal_type.data = next_step['meal']
                return redirect(url_for('daily_log_wizard', resident_id=resident_id))

            # Save form data to session
            if current_step == 1 and current_meal == 'breakfast':
                session['daily_log_wizard']['breakfast']['vitals'] = {
                    'systolic': form.systolic.data,
                    'diastolic': form.diastolic.data,
                    'pulse': form.pulse.data
                }
            elif current_step == 2:
                session['daily_log_wizard'][current_meal]['food'] = {
                    'intake_level': form.intake_level.data,
                    'notes': sanitize_input(form.notes.data) if form.intake_level.data == 'Other' else None
                }
            elif current_step == 3:
                session['daily_log_wizard'][current_meal]['liquid'] = {
                    'intake': form.liquid_intake.data
                }
            elif current_step == 4:
                session['daily_log_wizard'][current_meal]['bowel'] = {
                    'size': form.size.data,
                    'consistency': form.consistency.data
                }
            elif current_step == 5:
                session['daily_log_wizard'][current_meal]['urine'] = {
                    'output': form.urine_output.data
                }

            # If Submit on final step, save to database
            if form.submit.data and current_step_index == len(steps) - 1:
                # Save Vitals (breakfast only)
                if session['daily_log_wizard']['breakfast']['vitals']:
                    vitals = Vitals(
                        resident_id=resident_id,
                        date=today,
                        meal_type='breakfast',
                        systolic=session['daily_log_wizard']['breakfast']['vitals']['systolic'],
                        diastolic=session['daily_log_wizard']['breakfast']['vitals']['diastolic'],
                        pulse=session['daily_log_wizard']['breakfast']['vitals']['pulse']
                    )
                    db.session.add(vitals)

                # Save Food, Liquid, Bowel, Urine for each meal
                for meal in ['breakfast', 'lunch', 'dinner']:
                    # Food Intake
                    if session['daily_log_wizard'][meal]['food']:
                        food = FoodIntake(
                            resident_id=resident_id,
                            date=today,
                            meal_type=meal,
                            intake_level=session['daily_log_wizard'][meal]['food']['intake_level'],
                            notes=session['daily_log_wizard'][meal]['food']['notes']
                        )
                        db.session.add(food)
                    # Liquid Intake
                    if session['daily_log_wizard'][meal]['liquid']:
                        liquid = LiquidIntake(
                            resident_id=resident_id,
                            date=today,
                            meal_type=meal,
                            intake=session['daily_log_wizard'][meal]['liquid']['intake']
                        )
                        db.session.add(liquid)
                    # Bowel Movement
                    if session['daily_log_wizard'][meal]['bowel']:
                        bowel = BowelMovement(
                            resident_id=resident_id,
                            date=today,
                            meal_type=meal,
                            size=session['daily_log_wizard'][meal]['bowel']['size'],
                            consistency=session['daily_log_wizard'][meal]['bowel']['consistency']
                        )
                        db.session.add(bowel)
                    # Urine Output
                    if session['daily_log_wizard'][meal]['urine']:
                        urine = UrineOutput(
                            resident_id=resident_id,
                            date=today,
                            meal_type=meal,
                            output=session['daily_log_wizard'][meal]['urine']['output']
                        )
                        db.session.add(urine)

                db.session.commit()
                audit_log = AuditLog(user_id=current_user.id, action=f"Completed daily log for {resident.name}")
                db.session.add(audit_log)
                db.session.commit()
                session.pop('daily_log_wizard', None)  # Clear session
                flash('Daily log saved successfully.')
                return redirect(url_for('resident_profile', resident_id=resident_id))

            # Move to next step
            next_step_index = min(current_step_index + 1, len(steps) - 1)
            next_step = steps[next_step_index]
            form.step.data = str(next_step['id'])
            form.meal_type.data = next_step['meal']
            return redirect(url_for('daily_log_wizard', resident_id=resident_id))

        # Handle Back button
        if 'back' in request.form:
            prev_step_index = max(current_step_index - 1, 0)
            prev_step = steps[prev_step_index]
            form.step.data = str(prev_step['id'])
            form.meal_type.data = prev_step['meal']
            return redirect(url_for('daily_log_wizard', resident_id=resident_id))

    # Populate form with session data
    if current_step == 1 and current_meal == 'breakfast':
        form.systolic.data = session['daily_log_wizard']['breakfast']['vitals'].get('systolic')
        form.diastolic.data = session['daily_log_wizard']['breakfast']['vitals'].get('diastolic')
        form.pulse.data = session['daily_log_wizard']['breakfast']['vitals'].get('pulse')
    elif current_step == 2:
        form.intake_level.data = session['daily_log_wizard'][current_meal]['food'].get('intake_level')
        form.notes.data = session['daily_log_wizard'][current_meal]['food'].get('notes')
    elif current_step == 3:
        form.liquid_intake.data = session['daily_log_wizard'][current_meal]['liquid'].get('intake')
    elif current_step == 4:
        form.size.data = session['daily_log_wizard'][current_meal]['bowel'].get('size')
        form.consistency.data = session['daily_log_wizard'][current_meal]['bowel'].get('consistency')
    elif current_step == 5:
        form.urine_output.data = session['daily_log_wizard'][current_meal]['urine'].get('output')

    return render_template('daily_log_wizard.html', resident=resident, form=form, current_step=current_step, current_meal=current_meal, steps=steps, current_step_index=current_step_index)

@app.route('/resident/<int:resident_id>/daily-log-submit', methods=['POST'])
@login_required
def daily_log_submit(resident_id):
    if current_user.role not in ['admin', 'caregiver']:
        return jsonify({'error': 'Access denied'}), 403
    
    resident = Resident.query.get_or_404(resident_id)
    meal_type = request.form.get('meal_type')
    form_data = json.loads(request.form.get('form_data', '{}'))
    today = date.today()
    
    try:
        # Save Vitals (breakfast only)
        if meal_type == 'breakfast' and form_data.get('systolic') and form_data.get('diastolic') and form_data.get('pulse'):
            # Delete existing vitals for the day
            Vitals.query.filter_by(resident_id=resident_id, date=today, meal_type='breakfast').delete()
            
            vitals = Vitals(
                resident_id=resident_id,
                date=today,
                meal_type='breakfast',
                systolic=int(form_data['systolic']),
                diastolic=int(form_data['diastolic']),
                pulse=int(form_data['pulse'])
            )
            db.session.add(vitals)
        
        # Save Food Intake
        if form_data.get('intake_level'):
            # Delete existing food intake for the meal
            FoodIntake.query.filter_by(resident_id=resident_id, date=today, meal_type=meal_type).delete()
            
            food = FoodIntake(
                resident_id=resident_id,
                date=today,
                meal_type=meal_type,
                intake_level=form_data['intake_level'],
                notes=form_data.get('notes') if form_data.get('intake_level') == 'Other' else None
            )
            db.session.add(food)
        
        # Save Liquid Intake - Multiple entries
        # Delete existing liquid intakes for the meal
        LiquidIntake.query.filter_by(resident_id=resident_id, date=today, meal_type=meal_type).delete()
        
        # Save each liquid intake entry
        for i in range(1, 4):  # Liquid 1, 2, 3
            liquid_key = f'liquid_{i}'
            if form_data.get(liquid_key):
                liquid = LiquidIntake(
                    resident_id=resident_id,
                    date=today,
                    meal_type=meal_type,
                    intake=f"Liquid {i}: {form_data[liquid_key]}"
                )
                db.session.add(liquid)
        
        # Save Bowel Movement
        if form_data.get('size') and form_data.get('consistency'):
            # Delete existing bowel movement for the meal
            BowelMovement.query.filter_by(resident_id=resident_id, date=today, meal_type=meal_type).delete()
            
            bowel = BowelMovement(
                resident_id=resident_id,
                date=today,
                meal_type=meal_type,
                size=form_data['size'],
                consistency=form_data['consistency']
            )
            db.session.add(bowel)
        
        # Save Urine Output
        if form_data.get('urine_output'):
            # Delete existing urine output for the meal
            UrineOutput.query.filter_by(resident_id=resident_id, date=today, meal_type=meal_type).delete()
            
            urine = UrineOutput(
                resident_id=resident_id,
                date=today,
                meal_type=meal_type,
                output=form_data['urine_output']
            )
            db.session.add(urine)
        
        db.session.commit()
        
        # Audit log
        audit_log = AuditLog(user_id=current_user.id, action=f"Completed {meal_type} log for {resident.name}")
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/resident/<int:resident_id>/logs', methods=['GET', 'POST'])
@login_required
def daily_logs(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    date_str = request.args.get('date', date.today().isoformat())
    log_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    food_intakes = FoodIntake.query.filter_by(resident_id=resident_id, date=log_date).all()
    liquid_intakes = LiquidIntake.query.filter_by(resident_id=resident_id, date=log_date).all()
    bowel_movements = BowelMovement.query.filter_by(resident_id=resident_id, date=log_date).all()
    urine_outputs = UrineOutput.query.filter_by(resident_id=resident_id, date=log_date).all()
    vitals = Vitals.query.filter_by(resident_id=resident_id, date=log_date, meal_type='breakfast').first()

    missing_logs = []
    meal_types = ['breakfast', 'lunch', 'dinner']
    logged_meals = [food.meal_type for food in food_intakes]
    for meal in meal_types:
        if meal not in logged_meals:
            missing_logs.append(f"Missing {meal} log")

    prev_date = (log_date - timedelta(days=1)).isoformat()
    next_date = (log_date + timedelta(days=1)).isoformat()

    class DailyLogFoodIntakeForm(FlaskForm):
        meal_type = SelectField('Meal Type', choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner')], validators=[DataRequired()])
        description = StringField('Description', validators=[DataRequired()])
        submit = SubmitField('Add Food')

    class DailyLogLiquidIntakeForm(FlaskForm):
        liquid_type = StringField('Liquid Type', validators=[DataRequired()])
        amount = StringField('Amount', validators=[DataRequired()])
        submit = SubmitField('Add Liquid')

    class DailyLogBowelMovementForm(FlaskForm):
        size = SelectField('Size', choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')], validators=[DataRequired()])
        consistency = SelectField('Consistency', choices=[('Soft', 'Soft'), ('Medium', 'Medium'), ('Hard', 'Hard')], validators=[DataRequired()])
        submit = SubmitField('Add Bowel Movement')

    class DailyLogUrineOutputForm(FlaskForm):
        output = SelectField('Output', choices=[('Yes', 'Yes'), ('No', 'No'), ('No Output', 'No Output')], validators=[DataRequired()])
        submit = SubmitField('Add Urine Output')

    # Instantiate the forms
    food_form = DailyLogFoodIntakeForm()
    liquid_form = DailyLogLiquidIntakeForm()
    bowel_form = DailyLogBowelMovementForm()
    urine_form = DailyLogUrineOutputForm()

    if request.method == 'POST':
        if food_form.validate_on_submit() and 'add_food' in request.form and current_user.role in ['admin', 'caregiver']:
            meal_type = food_form.meal_type.data
            description = sanitize_input(food_form.description.data)
            if meal_type not in meal_types:
                flash('Invalid meal type')
                return redirect(url_for('daily_logs', resident_id=resident_id, date=log_date.isoformat()))
            new_food = FoodIntake(resident_id=resident_id, date=log_date, meal_type=meal_type, intake_level=description)
            db.session.add(new_food)
            db.session.commit()
            audit_log = AuditLog(user_id=current_user.id, action=f"Added food intake for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Food intake added successfully.')
        elif liquid_form.validate_on_submit() and 'add_liquid' in request.form and current_user.role in ['admin', 'caregiver']:
            liquid_type = sanitize_input(liquid_form.liquid_type.data)
            amount = sanitize_input(liquid_form.amount.data)
            new_liquid = LiquidIntake(resident_id=resident_id, date=log_date, meal_type='breakfast', intake=liquid_type or amount)
            db.session.add(new_liquid)
            db.session.commit()
            audit_log = AuditLog(user_id=current_user.id, action=f"Added liquid intake for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Liquid intake added successfully.')
        elif bowel_form.validate_on_submit() and 'add_bowel' in request.form and current_user.role in ['admin', 'caregiver']:
            size = bowel_form.size.data
            consistency = bowel_form.consistency.data
            if size not in ['Small', 'Medium', 'Large'] or consistency not in ['Soft', 'Medium', 'Hard']:
                flash('Invalid bowel movement data')
                return redirect(url_for('daily_logs', resident_id=resident_id, date=log_date.isoformat()))
            new_bowel = BowelMovement(resident_id=resident_id, date=log_date, meal_type='breakfast', size=size, consistency=consistency)
            db.session.add(new_bowel)
            db.session.commit()
            audit_log = AuditLog(user_id=current_user.id, action=f"Added bowel movement for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Bowel movement added successfully.')
        elif urine_form.validate_on_submit() and 'add_urine' in request.form and current_user.role in ['admin', 'caregiver']:
            output = urine_form.output.data
            if output not in ['Yes', 'No', 'No Output']:
                flash('Invalid urine output data')
                return redirect(url_for('daily_logs', resident_id=resident_id, date=log_date.isoformat()))
            new_urine = UrineOutput(resident_id=resident_id, date=log_date, meal_type='breakfast', output=output)
            db.session.add(new_urine)
            db.session.commit()
            audit_log = AuditLog(user_id=current_user.id, action=f"Added urine output for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Urine output added successfully.')
        return redirect(url_for('daily_logs', resident_id=resident_id, date=log_date.isoformat()))

    return render_template('daily_logs.html', resident=resident, log_date=log_date,
                          food_intakes=food_intakes, liquid_intakes=liquid_intakes,
                          bowel_movements=bowel_movements, urine_outputs=urine_outputs,
                          vitals=vitals, missing_logs=missing_logs, prev_date=prev_date, next_date=next_date,
                          food_form=food_form, liquid_form=liquid_form, bowel_form=bowel_form, urine_form=urine_form)

@app.route('/resident/<int:resident_id>/medications', methods=['GET', 'POST'])
@login_required
def medications(resident_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))

    resident = Resident.query.get_or_404(resident_id)
    medications = Medication.query.filter_by(resident_id=resident_id).all()
    medication_form = MedicationForm()
    log_form = MedicationLogForm()
    log_form.medication_id.choices = [(med.id, med.name) for med in medications]

    if request.method == 'POST':
        if medication_form.validate_on_submit() and 'add_medication' in request.form:
            name = sanitize_input(medication_form.name.data)
            dosage = sanitize_input(medication_form.dosage.data)
            frequency = sanitize_input(medication_form.frequency.data)
            notes = sanitize_input(medication_form.notes.data)
            form = sanitize_input(medication_form.form.data)
            common_uses = sanitize_input(medication_form.common_uses.data)
            start_date = medication_form.start_date.data
            end_date = medication_form.end_date.data
            if not name:
                flash('Medication name is required')
                return redirect(url_for('medications', resident_id=resident_id))
            new_med = Medication(resident_id=resident_id, name=name, dosage=dosage, frequency=frequency,
                                 notes=notes, form=form, common_uses=common_uses, start_date=start_date, end_date=end_date)
            db.session.add(new_med)
            # Add to MedicationCatalog if not already present
            if not MedicationCatalog.query.filter_by(name=name).first():
                catalog_entry = MedicationCatalog(name=name, default_dosage=dosage, default_frequency=frequency,
                                                 default_notes=notes, form=form, common_uses=common_uses)
                db.session.add(catalog_entry)
            db.session.commit()
            audit_log = AuditLog(user_id=current_user.id, action=f"Added medication {name} for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Medication added successfully.')
        elif log_form.validate_on_submit() and 'log_dose' in request.form:
            medication_id = log_form.medication_id.data
            time = datetime.strptime(log_form.time.data, '%H:%M').time()
            med_name = Medication.query.get(medication_id).name
            new_log = MedicationLog(medication_id=medication_id, resident_id=resident_id, date=date.today(), time=time, administered=True)
            db.session.add(new_log)
            db.session.commit()
            audit_log = AuditLog(user_id=current_user.id, action=f"Logged dose for {med_name} for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Dose logged successfully.')
        elif 'delete_medication' in request.form:
            medication_id = request.form['medication_id']
            medication = Medication.query.get_or_404(medication_id)
            med_name = medication.name
            db.session.delete(medication)
            db.session.commit()
            audit_log = AuditLog(user_id=current_user.id, action=f"Deleted medication {med_name} for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Medication deleted successfully.')
        return redirect(url_for('medications', resident_id=resident_id))

    medication_logs = MedicationLog.query.filter_by(resident_id=resident_id).all()
    return render_template('medications.html', resident=resident, medications=medications, medication_logs=medication_logs,
                          medication_form=medication_form, log_form=log_form)

@app.route('/resident/<int:resident_id>/documents', methods=['GET', 'POST'])
@login_required
def documents(resident_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))

    resident = Resident.query.get_or_404(resident_id)
    documents = Document.query.filter_by(resident_id=resident_id).all()
    form = DocumentForm()

    expired_documents = [doc for doc in documents if doc.expiration_date and doc.expiration_date < date.today()]

    if request.method == 'POST':
        if form.validate_on_submit() and 'add_document' in request.form:
            file = form.file.data
            name = sanitize_input(form.name.data)
            expiration_date = form.expiration_date.data
            if not file or not name:
                flash('File and name are required')
                return redirect(url_for('documents', resident_id=resident_id))
            if not (file.filename.endswith('.pdf') or file.filename.lower().endswith(('.jpg', '.jpeg', '.png'))):
                flash('Invalid file type. Only PDFs and images allowed.')
                return redirect(url_for('documents', resident_id=resident_id))
            try:
                filename = f"{resident_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                encrypted_filename = f"{filename}.enc"
                file_data = file.read()
                encrypted_data = cipher.encrypt(file_data)
                with open(os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename), 'wb') as f:
                    f.write(encrypted_data)
                new_doc = Document(resident_id=resident_id, filename=encrypted_filename, name=name, upload_date=date.today(), expiration_date=expiration_date)
                db.session.add(new_doc)
                db.session.commit()
                audit_log = AuditLog(user_id=current_user.id, action=f"Uploaded document {name} for {resident.name}")
                db.session.add(audit_log)
                db.session.commit()
                flash('Document uploaded successfully.')
            except Exception as e:
                flash(f'Failed to upload document: {str(e)}')
        elif 'delete_document' in request.form:
            document_id = request.form['document_id']
            document = Document.query.get_or_404(document_id)
            doc_name = document.name
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], document.filename))
            except OSError:
                pass
            db.session.delete(document)
            db.session.commit()
            audit_log = AuditLog(user_id=current_user.id, action=f"Deleted document {doc_name} for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Document deleted successfully.')
        return redirect(url_for('documents', resident_id=resident_id))

    return render_template('documents.html', resident=resident, documents=documents, expired_documents=expired_documents, form=form)

@app.route('/documents/<path:filename>')
@login_required
def serve_document(filename):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    try:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        original_filename = filename.replace('.enc', '')
        return send_file(
            BytesIO(decrypted_data),
            download_name=original_filename,
            as_attachment=True,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        flash(f'Failed to serve document: {str(e)}')
        return redirect(url_for('home'))

@app.route('/resident/<int:resident_id>/report', methods=['GET', 'POST'])
@login_required
def report(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    form = ReportForm()
    start_date = request.args.get('start_date', (date.today() - timedelta(days=7)).isoformat())
    end_date = request.args.get('end_date', date.today().isoformat())

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format')
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()

    food_intakes = FoodIntake.query.filter_by(resident_id=resident_id).filter(FoodIntake.date.between(start_date, end_date)).all()
    liquid_intakes = LiquidIntake.query.filter_by(resident_id=resident_id).filter(LiquidIntake.date.between(start_date, end_date)).all()
    bowel_movements = BowelMovement.query.filter_by(resident_id=resident_id).filter(BowelMovement.date.between(start_date, end_date)).all()
    urine_outputs = UrineOutput.query.filter_by(resident_id=resident_id).filter(UrineOutput.date.between(start_date, end_date)).all()
    medication_logs = MedicationLog.query.filter_by(resident_id=resident_id).filter(MedicationLog.date.between(start_date, end_date)).all()

    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    meal_counts = {d.isoformat(): {'breakfast': 0, 'lunch': 0, 'dinner': 0} for d in date_range}
    for food in food_intakes:
        date_str = food.date.isoformat()
        if date_str in meal_counts:
            meal_counts[date_str][food.meal_type] += 1
    chart_labels = [d.isoformat() for d in date_range]
    chart_data = {
        'breakfast': [meal_counts[d]['breakfast'] for d in chart_labels],
        'lunch': [meal_counts[d]['lunch'] for d in chart_labels],
        'dinner': [meal_counts[d]['dinner'] for d in chart_labels]
    }

    if form.validate_on_submit() and form.export_pdf.data:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        y = 750
        pdf.drawString(100, y, f"Report for {resident.name}: {start_date} to {end_date}")
        y -= 20
        pdf.drawString(100, y, "Food Intakes")
        y -= 20
        for food in food_intakes:
            pdf.drawString(120, y, f"{food.date} - {food.meal_type.capitalize()}: {food.intake_level or 'N/A'}")
            if food.notes:
                pdf.drawString(120, y - 15, f"Notes: {food.notes}")
                y -= 15
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        y -= 20
        pdf.drawString(100, y, "Liquid Intakes")
        y -= 20
        for liquid in liquid_intakes:
            pdf.drawString(120, y, f"{liquid.date} {liquid.meal_type.capitalize()}: {liquid.intake or 'N/A'}")
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        y -= 20
        pdf.drawString(100, y, "Bowel Movements")
        y -= 20
        pdf.drawString(100, y, "Bowel Movements")
        y -= 20
        for bowel in bowel_movements:
            pdf.drawString(120, y, f"{bowel.date} {bowel.meal_type.capitalize()}: Size - {bowel.size}, Consistency - {bowel.consistency}")
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        y -= 20
        pdf.drawString(100, y, "Urine Outputs")
        y -= 20
        for urine in urine_outputs:
            pdf.drawString(120, y, f"{urine.date} {urine.meal_type.capitalize()}: {urine.output}")
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        y -= 20
        pdf.drawString(100, y, "Medication Logs")
        y -= 20
        for log in medication_logs:
            med_name = Medication.query.get(log.medication_id).name
            pdf.drawString(120, y, f"{log.date} {log.time}: {med_name} - Administered")
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        safe_name = re.sub(r'[^\w\-]', '_', resident.name)
        return send_file(buffer, as_attachment=True, download_name=f"report_{safe_name}_{start_date}_to_{end_date}.pdf", mimetype='application/pdf')

    return render_template('report.html', resident=resident, start_date=start_date, end_date=end_date,
                          food_intakes=food_intakes, liquid_intakes=liquid_intakes,
                          bowel_movements=bowel_movements, urine_outputs=urine_outputs,
                          medication_logs=medication_logs, chart_labels=json.dumps(chart_labels),
                          chart_data=json.dumps(chart_data), form=form)

# Run the app and initialize database with sample data
if __name__ == '__main__':
    with app.app_context():
        print("Creating database at afh.db...")
        db.create_all()
        print("Database created!")
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='admin')
            db.session.add(admin)
            db.session.commit()
        if not User.query.filter_by(username='caregiver').first():
            caregiver = User(username='caregiver', password_hash=generate_password_hash('caregiver123'), role='caregiver')
            db.session.add(caregiver)
            db.session.commit()
        if not Resident.query.filter_by(name='John Doe').first():
            resident = Resident(name='John Doe', dob=date(1950, 1, 1), medical_info='Diabetic', emergency_contact='Jane Doe - 555-1234')
            db.session.add(resident)
            db.session.commit()
        sample_medications = [
            # Most commonly prescribed for elderly
            {'name': 'Lisinopril', 'default_dosage': '10 mg', 'default_frequency': 'Daily', 'default_notes': 'Monitor blood pressure', 'form': 'tablet', 'common_uses': 'hypertension, heart failure'},
            {'name': 'Metformin', 'default_dosage': '500 mg', 'default_frequency': 'Twice daily', 'default_notes': 'Take with meals', 'form': 'tablet', 'common_uses': 'type 2 diabetes'},
            {'name': 'Atorvastatin', 'default_dosage': '20 mg', 'default_frequency': 'Daily', 'default_notes': 'Take at bedtime', 'form': 'tablet', 'common_uses': 'high cholesterol'},
            {'name': 'Amlodipine', 'default_dosage': '5 mg', 'default_frequency': 'Daily', 'default_notes': 'Monitor for ankle swelling', 'form': 'tablet', 'common_uses': 'hypertension, angina'},
            {'name': 'Omeprazole', 'default_dosage': '20 mg', 'default_frequency': 'Daily', 'default_notes': 'Take before breakfast', 'form': 'capsule', 'common_uses': 'GERD, stomach ulcers'},
            {'name': 'Aricept', 'default_dosage': '10 mg', 'default_frequency': 'Daily', 'default_notes': 'Take at bedtime', 'form': 'tablet', 'common_uses': 'Alzheimer\'s disease'},
            {'name': 'Furosemide', 'default_dosage': '40 mg', 'default_frequency': 'Daily', 'default_notes': 'Monitor potassium levels', 'form': 'tablet', 'common_uses': 'heart failure, fluid retention'},
            {'name': 'Warfarin', 'default_dosage': '5 mg', 'default_frequency': 'Daily', 'default_notes': 'Regular INR monitoring required', 'form': 'tablet', 'common_uses': 'blood clot prevention'},
            {'name': 'Synthroid', 'default_dosage': '100 mcg', 'default_frequency': 'Daily', 'default_notes': 'Take on empty stomach', 'form': 'tablet', 'common_uses': 'hypothyroidism'},
            {'name': 'Acetaminophen', 'default_dosage': '325 mg', 'default_frequency': 'As needed', 'default_notes': 'Max 3000 mg daily', 'form': 'tablet', 'common_uses': 'pain relief, fever'},
            {'name': 'Gabapentin', 'default_dosage': '300 mg', 'default_frequency': 'Three times daily', 'default_notes': 'Gradual dose increase', 'form': 'capsule', 'common_uses': 'neuropathy, seizures'},
            {'name': 'Sertraline', 'default_dosage': '50 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with food', 'form': 'tablet', 'common_uses': 'depression, anxiety'},
            {'name': 'Fosamax', 'default_dosage': '70 mg', 'default_frequency': 'Weekly', 'default_notes': 'Take on empty stomach, remain upright 30 min', 'form': 'tablet', 'common_uses': 'osteoporosis'},
            {'name': 'Vitamin D3', 'default_dosage': '1000 IU', 'default_frequency': 'Daily', 'default_notes': 'Take with meals', 'form': 'tablet', 'common_uses': 'bone health, vitamin deficiency'},
            {'name': 'Calcium', 'default_dosage': '500 mg', 'default_frequency': 'Twice daily', 'default_notes': 'Take with food', 'form': 'tablet', 'common_uses': 'bone health'},
            {'name': 'Aspirin', 'default_dosage': '81 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with food', 'form': 'tablet', 'common_uses': 'heart protection, stroke prevention'},
            {'name': 'Sinemet', 'default_dosage': '25/100 mg', 'default_frequency': 'Three times daily', 'default_notes': 'Take with food if nausea occurs', 'form': 'tablet', 'common_uses': 'Parkinson\'s disease'},
            {'name': 'Donepezil', 'default_dosage': '10 mg', 'default_frequency': 'Daily', 'default_notes': 'Take at bedtime', 'form': 'tablet', 'common_uses': 'Alzheimer\'s disease'},
            {'name': 'Pantoprazole', 'default_dosage': '40 mg', 'default_frequency': 'Daily', 'default_notes': 'Take before breakfast', 'form': 'tablet', 'common_uses': 'GERD, stomach ulcers'},
            {'name': 'Tramadol', 'default_dosage': '50 mg', 'default_frequency': 'As needed', 'default_notes': 'Max 400 mg daily', 'form': 'tablet', 'common_uses': 'moderate pain'},
            {'name': 'Prednisone', 'default_dosage': '10 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with food, taper gradually', 'form': 'tablet', 'common_uses': 'inflammation, autoimmune conditions'},
            {'name': 'Carvedilol', 'default_dosage': '12.5 mg', 'default_frequency': 'Twice daily', 'default_notes': 'Take with food', 'form': 'tablet', 'common_uses': 'heart failure, high blood pressure'},
            {'name': 'Clopidogrel', 'default_dosage': '75 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with or without food', 'form': 'tablet', 'common_uses': 'blood clot prevention'},
            {'name': 'Metoprolol', 'default_dosage': '50 mg', 'default_frequency': 'Twice daily', 'default_notes': 'Monitor heart rate', 'form': 'tablet', 'common_uses': 'high blood pressure, heart failure'},
            {'name': 'Losartan', 'default_dosage': '50 mg', 'default_frequency': 'Daily', 'default_notes': 'Monitor potassium levels', 'form': 'tablet', 'common_uses': 'high blood pressure'},
            {'name': 'Hydrochlorothiazide', 'default_dosage': '25 mg', 'default_frequency': 'Daily', 'default_notes': 'Monitor electrolytes', 'form': 'tablet', 'common_uses': 'high blood pressure, fluid retention'},
            {'name': 'Glipizide', 'default_dosage': '5 mg', 'default_frequency': 'Twice daily', 'default_notes': 'Take before meals', 'form': 'tablet', 'common_uses': 'type 2 diabetes'},
            {'name': 'Allopurinol', 'default_dosage': '300 mg', 'default_frequency': 'Daily', 'default_notes': 'Take after meals', 'form': 'tablet', 'common_uses': 'gout prevention'},
            {'name': 'Tamsulosin', 'default_dosage': '0.4 mg', 'default_frequency': 'Daily', 'default_notes': 'Take 30 min after same meal daily', 'form': 'capsule', 'common_uses': 'enlarged prostate'},
            {'name': 'Finasteride', 'default_dosage': '5 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with or without food', 'form': 'tablet', 'common_uses': 'enlarged prostate'},
            {'name': 'Latanoprost', 'default_dosage': '0.005%', 'default_frequency': 'Daily at bedtime', 'default_notes': 'One drop in affected eye', 'form': 'eye drops', 'common_uses': 'glaucoma'},
            {'name': 'Levothyroxine', 'default_dosage': '100 mcg', 'default_frequency': 'Daily', 'default_notes': 'Take on empty stomach', 'form': 'tablet', 'common_uses': 'hypothyroidism'},
            {'name': 'Escitalopram', 'default_dosage': '10 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with or without food', 'form': 'tablet', 'common_uses': 'depression, anxiety'},
            {'name': 'Fluoxetine', 'default_dosage': '20 mg', 'default_frequency': 'Daily', 'default_notes': 'Take in morning', 'form': 'capsule', 'common_uses': 'depression, anxiety'},
            {'name': 'Trazodone', 'default_dosage': '50 mg', 'default_frequency': 'At bedtime', 'default_notes': 'Take with food', 'form': 'tablet', 'common_uses': 'depression, insomnia'},
            {'name': 'Lorazepam', 'default_dosage': '0.5 mg', 'default_frequency': 'As needed', 'default_notes': 'Use cautiously in elderly', 'form': 'tablet', 'common_uses': 'anxiety, insomnia'},
            {'name': 'Zolpidem', 'default_dosage': '5 mg', 'default_frequency': 'At bedtime', 'default_notes': 'Use lowest effective dose', 'form': 'tablet', 'common_uses': 'insomnia'},
            {'name': 'Simvastatin', 'default_dosage': '40 mg', 'default_frequency': 'Daily at bedtime', 'default_notes': 'Monitor for muscle pain', 'form': 'tablet', 'common_uses': 'high cholesterol'},
            {'name': 'Digoxin', 'default_dosage': '0.25 mg', 'default_frequency': 'Daily', 'default_notes': 'Monitor drug levels', 'form': 'tablet', 'common_uses': 'heart failure, atrial fibrillation'},
            {'name': 'Spironolactone', 'default_dosage': '25 mg', 'default_frequency': 'Daily', 'default_notes': 'Monitor potassium levels', 'form': 'tablet', 'common_uses': 'heart failure, high blood pressure'},
            {'name': 'Potassium', 'default_dosage': '10 mEq', 'default_frequency': 'Daily', 'default_notes': 'Take with food', 'form': 'tablet', 'common_uses': 'potassium deficiency'},
            {'name': 'Iron', 'default_dosage': '325 mg', 'default_frequency': 'Daily', 'default_notes': 'Take on empty stomach if tolerated', 'form': 'tablet', 'common_uses': 'iron deficiency anemia'},
            {'name': 'Multivitamin', 'default_dosage': '1 tablet', 'default_frequency': 'Daily', 'default_notes': 'Take with breakfast', 'form': 'tablet', 'common_uses': 'nutritional supplement'},
            {'name': 'Fish Oil', 'default_dosage': '1000 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with meals', 'form': 'capsule', 'common_uses': 'heart health, inflammation'},
            {'name': 'Celecoxib', 'default_dosage': '200 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with food', 'form': 'capsule', 'common_uses': 'arthritis pain, inflammation'},
            {'name': 'Meloxicam', 'default_dosage': '7.5 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with food', 'form': 'tablet', 'common_uses': 'arthritis pain, inflammation'},
            {'name': 'Duloxetine', 'default_dosage': '60 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with food', 'form': 'capsule', 'common_uses': 'depression, anxiety, neuropathy'},
            {'name': 'Pregabalin', 'default_dosage': '150 mg', 'default_frequency': 'Twice daily', 'default_notes': 'Gradual dose titration', 'form': 'capsule', 'common_uses': 'neuropathy, fibromyalgia'},
            {'name': 'Venlafaxine', 'default_dosage': '75 mg', 'default_frequency': 'Daily', 'default_notes': 'Take with food', 'form': 'capsule', 'common_uses': 'depression, anxiety'},
            {'name': 'Mirtazapine', 'default_dosage': '15 mg', 'default_frequency': 'At bedtime', 'default_notes': 'May cause drowsiness', 'form': 'tablet', 'common_uses': 'depression'},
            {'name': 'Quetiapine', 'default_dosage': '25 mg', 'default_frequency': 'At bedtime', 'default_notes': 'Start with low dose', 'form': 'tablet', 'common_uses': 'bipolar disorder, schizophrenia'},
            {'name': 'Risperidone', 'default_dosage': '1 mg', 'default_frequency': 'Twice daily', 'default_notes': 'Monitor for side effects', 'form': 'tablet', 'common_uses': 'schizophrenia, bipolar disorder'}
        ]
        for med in sample_medications:
            if not MedicationCatalog.query.filter_by(name=med['name']).first():
                db.session.add(MedicationCatalog(**med))
        db.session.commit()
    
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)