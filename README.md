# Tour Packages Project Setup and Deployment Guide

## **Project Overview**
- **Programming Language:** Python
- **Framework:** Django (Web Framework)
- **Database:** PostgreSQL (PSQL)
- **Payment Integration:** Stripe

---

## **Project Setup Instructions**

### **1. Clone the Project Repository**
   Open a terminal and run the following commands:
   ```bash
   git clone <https://github.com/navamidr/Ecommerce-Tour-Packages.git>
   cd <Ecommerce-Tour-Packages>
   ```

### **2. Set Up a Virtual Environment**
   - Create a virtual environment:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - **Windows:**
       ```bash
       venv\Scripts\activate
       ```
     - **Linux/Mac:**
       ```bash
       source venv/bin/activate
       ```

### **3. Install Dependencies**
   Run the following command to install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### **4. Configure Environment Variables**
   Create a `.env` file in the root directory (if not already present) and set necessary environment variables like:
   ```env
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1, localhost
   DATABASE_URL=postgres://<user>:<password>@<host>:<port>/<database_name>

   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   
   YOUR_DOMAIN=http://localhost:8000
   
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_password
   DEFAULT_FROM_EMAIL=your_email@gmail.com
   ```

### **5. Set Up PostgreSQL Database**
   Ensure PostgreSQL is installed and create a database for the project.
   ```bash
   sudo -u postgres psql
   CREATE DATABASE tour_packages_db;
   CREATE USER tour_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE tour_packages_db TO tour_user;
   \q
   ```

### **6. Apply Database Migrations**
   ```bash
   python manage.py migrate
   ```

### **7. Create Superuser for Admin Access**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set up the admin credentials.

### **8. Configure Email Backend and Stripe Integration**

   In your `settings.py`, include the following configurations:

   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = env.str('EMAIL_HOST', default='smtp.gmail.com')
   EMAIL_PORT = env.int('EMAIL_PORT', default=587)
   EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
   EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default=False)
   EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
   DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='your_email@gmail.com')

   STRIPE_SECRET_KEY = env.str("STRIPE_SECRET_KEY")
   STRIPE_PUBLISHABLE_KEY = env.str("STRIPE_PUBLISHABLE_KEY")

   YOUR_DOMAIN = env.str("YOUR_DOMAIN", default="http://localhost:8000")
   ```

### **9. Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## **Additional Notes**
- Ensure environment variables are properly configured for production environments.
- For secure deployment, set `DEBUG=False` and configure `ALLOWED_HOSTS` correctly.
- Test Stripe payment flow and email notifications thoroughly before production.

This guide should help you set up, run, and deploy your Django-based Tour Packages project efficiently. Happy coding!

