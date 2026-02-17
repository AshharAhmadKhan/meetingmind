def lambda_handler(event, context):
    """
    Cognito Pre-Signup trigger
    Auto-confirms user but they remain disabled until manually approved
    """
    # Auto-confirm the user (skip email verification code)
    event['response']['autoConfirmUser'] = True
    event['response']['autoVerifyEmail'] = True
    
    return event
