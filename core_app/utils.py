from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone


def send_login_email(user, request=None):
    """Send a login notification email to the user."""
    login_time = timezone.now().strftime('%B %d, %Y at %H:%M:%S UTC')
    
    # Try to get IP address from request
    ip_address = 'Unknown'
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown')

    message = f"""
    Dear {user.first_name or user.username},

    We detected a successful login to your Avalanch Metal account.

    Login Details:
    - Date & Time: {login_time}
    - IP Address: {ip_address}
    - Username: {user.username}

    If this was you, no further action is needed.

    If you did not log in, please secure your account immediately by changing your password and contacting our support team at support@avalanchmetal.com.

    Best regards,
    The Avalanch Metal Team
    """

    try:
        send_mail(
            'Login Notification - Avalanch Metal',
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'support@avalanchmetal.com',
            [user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending login email: {e}")


def send_registration_email(user):
    """Send a welcome email to newly registered users."""
    message = f"""
    Dear {user.first_name or user.username},

    Welcome to Avalanch Metal! Your account has been successfully created.

    Account Details:
    - Username: {user.username}
    - Email: {user.email}
    - Registration Date: {timezone.now().strftime('%B %d, %Y')}

    Here's what you can do next:
    - Fund your account and start investing in gold
    - Explore our investment plans for daily returns
    - Trade gold shares backed by physical assets
    - Complete KYC verification to enable withdrawals

    If you have any questions, our support team is available 24/7 at support@avalanchmetal.com.

    Thank you for choosing Avalanch Metal. We look forward to helping you grow your wealth.

    Best regards,
    The Avalanch Metal Team
    """

    try:
        send_mail(
            'Welcome to Avalanch Metal!',
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'support@avalanchmetal.com',
            [user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending registration email: {e}")

def send_transaction_email(user, transaction):
    subject = f"Transaction Notification: {transaction.transaction_type.capitalize()}"
    
    context = {
        'user': user,
        'transaction': transaction,
        'balance': user.account.balance
    }
    
    # We could use templates for cleaner emails if they exist.
    # For now, let's just use a simple string logic.
    
    message = f"""
    Dear {user.first_name or user.username},

    A {transaction.transaction_type} of {transaction.amount} has been successfully processed on your account.

    Transaction Details:
    - Type: {transaction.transaction_type.capitalize()}
    - Amount: {transaction.amount}
    - Status: {transaction.status.capitalize()}
    - Reference: {transaction.reference}
    - Date: {transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

    Your current account balance is: {user.account.balance}

    Thank you for choosing Avalanch Metal.

    Best regards,
    The Avalanch Metal Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'support@avalanchmetal.com',
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")

def send_transaction_request_email(user, request_type, amount, withdrawal=None):
    subject = f"Transaction Request Received: {request_type.capitalize()}"
    
    wallet_details = ""
    if request_type == 'withdrawal' and withdrawal:
        wallet_name = f"\n    - Wallet Name: {withdrawal.wallet_name}" if withdrawal.wallet_name else ""
        wallet_details = f"""
    Withdrawal Details:{wallet_name}
    - Wallet Address: {withdrawal.wallet_address}
    - Network: {withdrawal.network}"""

    message = f"""
    Dear {user.first_name or user.username},

    We have received your {request_type} request for {amount}.{wallet_details}

    Our team is currently verifying the transaction. You will receive another notification once it has been processed and credited/debited from your balance.

    Thank you for choosing Avalanch Metal.

    Best regards,
    The Avalanch Metal Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'support@avalanchmetal.com',
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending request email: {e}")


def send_investment_email(user, investment_type, investment_name, amount, units=None, price=None):
    """
    Send email notification for investment purchases.
    
    Args:
        user: The user making the investment
        investment_type: 'share', 'project', or 'plan'
        investment_name: Name of the asset/project/plan
        amount: Investment amount
        units: Number of units purchased (for shares)
        price: Unit price (for shares)
    """
    type_labels = {
        'share': 'Share Purchase',
        'project': 'Project Investment',
        'plan': 'Investment Plan Subscription'
    }
    
    subject = f"Investment Confirmation: {type_labels.get(investment_type, 'Investment')}"
    
    # Build investment details based on type
    if investment_type == 'share' and units and price:
        investment_details = f"""
    Investment Type: Share/Asset Purchase
    Asset: {investment_name}
    Amount Invested: ${amount:,.2f}
    Units Purchased: {float(units):.4f}
    Price per Unit: ${price:,.2f}"""
    elif investment_type == 'project':
        investment_details = f"""
    Investment Type: Project Investment
    Project: {investment_name}
    Amount Invested: ${amount:,.2f}"""
    elif investment_type == 'plan':
        investment_details = f"""
    Investment Type: Investment Plan
    Plan: {investment_name}
    Amount Invested: ${amount:,.2f}"""
    else:
        investment_details = f"""
    Investment: {investment_name}
    Amount Invested: ${amount:,.2f}"""
    
    message = f"""
    Dear {user.first_name or user.username},

    Congratulations! Your investment has been successfully processed.
    {investment_details}

    Your updated account balance is: ${user.account.balance:,.2f}

    You can track your investment performance in your dashboard.

    Thank you for investing with Avalanch Metal. We're committed to helping you grow your wealth.

    Best regards,
    The Avalanch Metal Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'support@avalanchmetal.com',
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending investment email: {e}")

