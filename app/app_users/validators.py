import re

def validar_email(email):

    # correos aceptados
    correos = [
        '@gmail.com',
        '@hotmail.com',
        '@outlook.com',
        '@outlook.es',
    ]

    for correo in correos:
        ext = re.findall(correo, email)
        if len(ext) == 1:
            last_string = re.search(correo, email).end()
            if len(email) == last_string:
                user_email = email.replace(correo,'')
                if len(user_email) > 5 and len(user_email) < 50:
                    if re.match("^[a-zA-Z0-9_.-]+$", user_email) is not None:
                        return False # Email no valido

    else:
        return True #Email válido



