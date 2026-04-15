## smart-inventory-management system
# Overview

      The Smart Inventory Management System (SIMS) is a web-based application developed to improve inventory handling in supermarkets. Traditional inventory systems rely heavily on manual processes, which often lead to errors, delays, and lack of real-time visibility.

      This system introduces an automated and intelligent approach to inventory management by continuously monitoring stock levels and product expiry dates. It provides timely notifications to administrators and suppliers, helping businesses make proactive decisions and reduce operational inefficiencies.

# Features
   Real-time monitoring of product stock levels
   Detection of understock and overstock conditions
   Expiry date tracking with advance alerts
   Automated notifications using AWS SNS (SMS and email)
   Reorder request management with approval and rejection functionality
   Centralized admin dashboard for monitoring system status
   Secure login and session management
   System Architecture

# The application follows a three-tier architecture:

    Presentation Layer: User interface built using HTML, CSS, and JavaScript
    Application Layer: Backend logic implemented using Flask (Python)
    Data Layer: MySQL database hosted on AWS RDS

The architecture enables seamless interaction between the web application, database, and notification services, ensuring scalability and efficiency.

# Modules

The system is divided into the following modules:

    User Authentication Module
    Inventory Management Module
    Notification Module (AWS SNS Integration)
    Reorder Management Module
    Expiry Monitoring Module
    Dashboard and Reporting Module
    Database Connection Module
    Session and Logout Module
    
# Technology Stack
    Frontend: HTML, CSS, JavaScript
    Backend: Python (Flask)
    Database: MySQL (AWS RDS)
    Cloud Services: AWS EC2, AWS SNS
    Operating System: Amazon Linux 2

## Installation and Setup
    
# Clone the repository
    git clone https://github.com/your-username/smart-inventory-system.git
    cd smart-inventory-system

# Install dependencies
    pip install flask mysql-connector-python boto3
    
## Configure database

# Update the database configuration in the application:

    DB_HOST = "your-rds-endpoint"
    DB_USER = "username"
    DB_PASSWORD = "password"
    DB_NAME = "database_name"
    Configure AWS SNS
    AWS_REGION = "your-region"
    SNS_TOPIC_ARN = "your-topic-arn"

# Run the application
    python app.py

# Key Benefits
    Improves inventory accuracy through automation
    Provides real-time visibility of stock levels
    Reduces product wastage due to expiry
    Enhances communication with suppliers
    Minimizes manual effort and operational delays
    Scalable and secure cloud-based solution
    Future Enhancements
    Integration of barcode and QR code scanning
    Mobile application for remote monitoring
    Predictive analytics using machine learning
    Role-based access control
    Advanced reporting and analytics
    Bulk data import/export support
    Integration with POS systems

## Conclusion

      The Smart Inventory Management System provides a structured and efficient solution to modern inventory challenges in supermarkets. By combining automation, real-time monitoring, and cloud-based communication, the system significantly improves operational efficiency and decision-making.
