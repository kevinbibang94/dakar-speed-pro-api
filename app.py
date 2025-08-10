from flask import Flask, request, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import os
import random
import string

app = Flask(__name__)

# 📂 Création du dossier pour les PDF si inexistant
if not os.path.exists('static/pdfs'):
    os.makedirs('static/pdfs')

# 📂 Dossier images pour le logo
LOGO_PATH = os.path.join('static', 'images', 'Dsp_logo-1.png')

# 📌 Fonction pour générer le PDF
def generate_delivery_pdf(data, tracking_code, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Logo
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, 1.5*cm, height - 4*cm, width=4*cm, preserveAspectRatio=True, mask='auto')

    # Titre + Code suivi
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 2*cm, "BON DE LIVRAISON")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 2*cm, height - 2*cm, f"Code suivi : {tracking_code}")

    # Ligne séparation
    c.line(1.5*cm, height - 2.5*cm, width - 1.5*cm, height - 2.5*cm)

    # Corps
    y = height - 5*cm
    c.setFont("Helvetica", 12)

    # Type de livraison
    delivery_type = data.get("delivery_type", "classique")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, f"Type de livraison : {delivery_type.capitalize()}")
    y -= 1.2*cm
    c.setFont("Helvetica", 12)

    # Champs communs
    common_fields = [
        ("Adresse de récupération :", data.get("pickup_address", "")),
        ("Adresse de livraison :", data.get("delivery_address", ""))
    ]

    # Champs spécifiques
    if delivery_type == "classique":
        common_fields.append(("Description du colis :", data.get("package_description", "")))
        common_fields.append(("Destinataire :", data.get("recipient_info", "")))

    elif delivery_type == "repas":
        common_fields.extend([
            ("Nom et adresse du restaurant :", data.get("restaurant_info", "")),
            ("Nom et adresse du client :", data.get("client_info", "")),
            ("Détails de la commande :", data.get("order_details", ""))
        ])

    elif delivery_type == "entreprise":
        common_fields.extend([
            ("Type de colis / unités :", data.get("package_type", "")),
            ("Heure souhaitée :", data.get("pickup_time", "")),
            ("Référence interne :", data.get("reference_internal", "")),
            ("Destinataire :", data.get("recipient_info", ""))
        ])

    # Affichage
    for label, value in common_fields:
        c.drawString(2*cm, y, f"• {label}")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(8*cm, y, value)
        y -= 1*cm
        c.setFont("Helvetica", 12)

    # Date
    c.line(1.5*cm, y, width - 1.5*cm, y)
    y -= 1*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, f"Date de génération : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    c.save()

# 📌 Endpoint pour générer le PDF
@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()

    # Génération code suivi
    tracking_code = "DSP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Génération du fichier PDF
    pdf_filename = f"bon_livraison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join('static', 'pdfs', pdf_filename)

    generate_delivery_pdf(data, tracking_code, pdf_path)

    # URL complète pour Twilio
    pdf_url = request.host_url + f"static/pdfs/{pdf_filename}"

    return jsonify({
        "tracking_code": tracking_code,
        "pdf_url": pdf_url
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
