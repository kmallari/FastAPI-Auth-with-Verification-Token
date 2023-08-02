"""
This module provides utility functions for user authentication and token generation.

Functions:
    verification_email_template(code: str) -> str:
        Generate an HTML template for the verification email containing the provided code.

    send_email(recipient: str, code: str) -> dict:
        Send an email to the specified recipient containing the verification code.

    get_hashed_password(password: str) -> str:
        Hash the provided password using the bcrypt algorithm.

    verify_password(password: str, hashed_pass: str) -> bool:
        Verify the provided password against the hashed password.

    get_expires_delta(expires_delta: int = None) -> datetime:
        Get the expiration time for access and refresh tokens.

    create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
        Create an access token for the specified subject.

    create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
        Create a refresh token for the specified subject.

Constants:
    ACCESS_TOKEN_EXPIRE_MINUTES (int): The default expiration time for access tokens in minutes.
    REFRESH_TOKEN_EXPIRE_MINUTES (int): The default expiration time for refresh tokens in minutes.
    ALGORITHM (str): The algorithm used for encoding tokens.
    JWT_SECRET_KEY (str): The secret key used for encoding access tokens.
    JWT_REFRESH_SECRET_KEY (str): The secret key used for encoding refresh tokens.
    WEBSITE_NAME (str): The name of the website used in the verification email.

Global Variables:
    password_context (CryptContext): An instance of CryptContext for hashing passwords.

Note:
    The JWT_SECRET_KEY and JWT_REFRESH_SECRET_KEY should be kept secret and stored securely,
    as they are crucial for token generation and decoding.

"""

import os
from datetime import datetime, timedelta
from typing import Dict
from typing import Optional
from typing import Union, Any

import sendgrid
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from passlib.context import CryptContext
from sendgrid.helpers.mail import Mail, Email, To, Content

from src.constants import SENDGRID_API_KEY, SENDGRID_EMAIL, CLIENT_URL

ACCESS_TOKEN_EXPIRE_MINUTES = 99999999  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET_KEY"]  # should be kept secret
WEBSITE_NAME = "cashr"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verification_email_template(code: str):
    """
    Generate an HTML template for the verification email containing the provided code.

    Parameters:
        code (str): The verification code to be included in the email template.

    Returns:
        str: The HTML template with the verification code included.
    """
    return f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="x-ua-compatible" content="ie=edge" />
    <title>Email Confirmation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style type="text/css">
      /**
   * Google webfonts. Recommended to include the .woff version for cross-client compatibility.
   */
      @media screen {{
    @ font-face {{
    font-family: "Source Sans Pro";
    font-style: normal;
    font-weight: 400;
    src: local("Source Sans Pro Regular"), local("SourceSansPro-Regular"),
    url(https: // fonts.gstatic.com/s/sourcesanspro/v10/ODelI1aHBYDBqgeIAH2zlBM0YzuT7MdOe03otPbuUS0.woff)
    format("woff");
    }}
    @ font-face {{
    font-family: "Source Sans Pro";
    font-style: normal;
    font-weight: 700;
    src: local("Source Sans Pro Bold"), local("SourceSansPro-Bold"),
    url(https: // fonts.gstatic.com/s/sourcesanspro/v10/toadOcfmlt9b38dHJxOBGFkQc6VGVFSmCnC_l7QZG60.woff)
    format("woff");
    }}
    }}
      /**
   * Avoid browser level font resizing.
   * 1. Windows Mobile
   * 2. iOS / OSX
   */
      body,
      table,
      td,
      a {{
    -ms - text - size - adjust: 100%; /* 1 */
        -webkit-text-size-adjust: 100%; /* 2 */
      }}
      /**
   * Remove extra space added to tables and cells in Outlook.
   */
      table,
      td {{
    mso - table - rspace: 0pt;
        mso-table-lspace: 0pt;
      }}
      /**
   * Better fluid images in Internet Explorer.
   */
      img {{
    -ms - interpolation - mode: bicubic;
      }}
      /**
   * Remove blue links for iOS devices.
   */
      a[x-apple-data-detectors] {{
    font - family: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
        color: inherit !important;
        text-decoration: none !important;
      }}
      /**
   * Fix centering issues in Android 4.4.
   */
      div[style*="margin: 16px 0;"] {{
    margin: 0 !important;
      }}
      body {{
    width: 100% !important;
        height: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
      }}
      /**
   * Collapse table borders to avoid space between cells.
   */
      table {{
    border - collapse: collapse !important;
      }}
      a {{
    color: #1a82e2;
      }}
      img {{
    height: auto;
        line-height: 100%;
        text-decoration: none;
        border: 0;
        outline: none;
      }}
    </style>
  </head>
  <body style="background-color: #e9ecef">
    <!-- start preheader -->
    <div
      class="preheader"
      style="
        display: none;
        max-width: 0;
        max-height: 0;
        overflow: hidden;
        font-size: 1px;
        line-height: 1px;
        color: #fff;
        opacity: 0;
      "
    >
      Verify your account in https://{WEBSITE_NAME}.klukode.dev using the code in this
      email
    </div>
    <!-- end preheader -->

    <!-- start body -->
    <table border="0" cellpadding="0" cellspacing="0" width="100%">
      <!-- start hero -->
      <tr>
        <td align="center" bgcolor="#e9ecef" style="padding-top: 96px">
          <!--[if (gte mso 9)|(IE)]>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600">
        <tr>
        <td align="center" valign="top" width="600">
        <![endif]-->
          <table
            border="0"
            cellpadding="0"
            cellspacing="0"
            width="100%"
            style="max-width: 480px"
          >
            <tr>
              <td
                align="left"
                bgcolor="#ffffff"
                style="
                  padding: 36px 24px 0;
                  font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif;
                  border-top: 3px solid #d4dadf;
                "
              >
                <h1
                  style="
                    margin: 0;
                    font-size: 32px;
                    font-weight: 700;
                    letter-spacing: -1px;
                    line-height: 48px;
                  "
                >
                  Confirm Your Account
                </h1>
              </td>
            </tr>
          </table>
          <!--[if (gte mso 9)|(IE)]>
        </td>
        </tr>
        </table>
        <![endif]-->
        </td>
      </tr>
      <!-- end hero -->

      <!-- start copy block -->
      <tr>
        <td align="center" bgcolor="#e9ecef">
          <!--[if (gte mso 9)|(IE)]>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600">
        <tr>
        <td align="center" valign="top" width="600">
        <![endif]-->
          <table
            border="0"
            cellpadding="0"
            cellspacing="0"
            width="100%"
            style="max-width: 480px"
          >
            <!-- start copy -->
            <tr>
              <td
                align="left"
                bgcolor="#ffffff"
                style="
                  padding: 24px;
                  font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif;
                  font-size: 16px;
                  line-height: 24px;
                "
              >
                <p style="margin: 0">
                  Tap the button below to verify your account. If you didn't
                  create an account with
                  <a href="{CLIENT_URL}">{WEBSITE_NAME}</a>, you can safely
                  delete this email.
                </p>
              </td>
            </tr>
            <!-- end copy -->

            <!-- start button -->
            <tr>
              <td align="left" bgcolor="#ffffff">
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                  <tr>
                    <td align="center" bgcolor="#ffffff" style="padding: 12px">
                      <table border="0" cellpadding="0" cellspacing="0">
                        <tr>
                          <td
                            align="center"
                            bgcolor="#1a82e2"
                            style="border-radius: 6px"
                          >
                            <a
                              href="{CLIENT_URL}/verify-account?code={code}"
                              target="_blank"
                              style="
                                display: inline-block;
                                padding: 16px 36px;
                                font-family: 'Source Sans Pro', Helvetica, Arial,
                                  sans-serif;
                                font-size: 16px;
                                color: #ffffff;
                                text-decoration: none;
                                border-radius: 6px;
                              "
                              >Verify Account</a
                            >
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <!-- end button -->

            <!-- start copy -->
            <tr>
              <td
                align="left"
                bgcolor="#ffffff"
                style="
                  padding: 24px;
                  font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif;
                  font-size: 16px;
                  line-height: 24px;
                "
              >
                <p style="margin: 0">
                  If that doesn't work, copy and paste the following code in the
                  account verification page:
                </p>
              </td>
            </tr>
            <!-- end copy -->

            <tr>
              <td
                align="left"
                bgcolor="#ffffff"
                style="
                  font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif;
                  font-size: 16px;
                  line-height: 24px;
                "
              >
                <h2 style="text-align: center; margin: 0">{code}</h2>
              </td>
            </tr>

            <!-- start copy -->
            <tr>
              <td
                align="left"
                bgcolor="#ffffff"
                style="
                  padding: 24px;
                  font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif;
                  font-size: 16px;
                  line-height: 24px;
                  border-bottom: 3px solid #d4dadf;
                "
              >
                <p style="margin: 0">
                  Cheers,<br />
                  cashr Team
                </p>
              </td>
            </tr>
            <!-- end copy -->
          </table>
          <!--[if (gte mso 9)|(IE)]>
        </td>
        </tr>
        </table>
        <![endif]-->
        </td>
      </tr>
      <!-- end copy block -->

      <!-- start footer -->
      <tr>
        <td align="center" bgcolor="#e9ecef" style="padding: 24px">
          <!--[if (gte mso 9)|(IE)]>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600">
        <tr>
        <td align="center" valign="top" width="600">
        <![endif]-->
          <table
            border="0"
            cellpadding="0"
            cellspacing="0"
            width="100%"
            style="max-width: 480px"
          >
            <!-- start permission -->
            <tr>
              <td
                align="center"
                bgcolor="#e9ecef"
                style="
                  padding: 12px 24px;
                  font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif;
                  font-size: 14px;
                  line-height: 20px;
                  color: #666;
                "
              >
                <p style="margin: 0">
                  You received this email because we received a request for
                  creation and verification for your account. If you didn't
                  request creation and verification, you can safely delete this
                  email.
                </p>
              </td>
            </tr>
            <!-- end permission -->
          </table>
          <!--[if (gte mso 9)|(IE)]>
        </td>
        </tr>
        </table>
        <![endif]-->
        </td>
      </tr>
      <!-- end footer -->
    </table>
    <!-- end body -->
  </body>
</html>
"""


async def send_email(recipient: str, code: str):
    """
    Email to the specified recipient containing the verification code.

    Parameters:
        recipient (str): The email address of the recipient.
        code (str): The verification code to be included in the email.

    Returns:
        dict: A dictionary containing the response from the email service.

    Raises:
        Any errors raised by the email service.
    """
    sendgrid_client = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(SENDGRID_EMAIL)  # Change to your verified sender
    to_email = To(recipient)  # Change to your recipient
    subject = "cashr Account Verification Code"
    # send html content
    content = Content(
        "text/html",
        # verification_email_template(code),
        verification_email_template(code),
    )
    mail = Mail(from_email, to_email, subject, content)
    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()
    # Send an HTTP POST request to /mail/send
    response = sendgrid_client.client.mail.send.post(request_body=mail_json)
    return {"res": response}


def get_hashed_password(password: str) -> str:
    """
    Hash the provided password using the bcrypt algorithm.

    Parameters:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """
    Verify the provided password against the hashed password.

    Parameters:
        password (str): The password to be verified.
        hashed_pass (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    return password_context.verify(password, hashed_pass)


def get_expires_delta(expires_delta: int = None) -> datetime:
    """
    Get the expiration time for access and refresh tokens.

    Parameters:
        expires_delta (int, optional): The time delta in minutes to set the expiration.
            If None, the default expiration value will be used.

    Returns:
        datetime: The expiration datetime for the token.
    """
    if expires_delta is not None:
        return datetime.utcnow() + expires_delta
    return datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
    Create an access token for the specified subject.

    Parameters:
        subject (Union[str, Any]): The subject for whom the token is being created.
        expires_delta (int, optional): The time delta in minutes to set the expiration.
            If None, the default expiration value will be used.

    Returns:
        str: The encoded access token.
    """
    expires_delta = get_expires_delta(expires_delta)
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """ "
    Create a refresh token for the specified subject.

    Parameters:
        subject (Union[str, Any]): The subject for whom the token is being created.
        expires_delta (int, optional): The time delta in minutes to set the expiration.
            If None, the default expiration value will be used.

    Returns:
        str: The encoded refresh token.
    """
    expires_delta = get_expires_delta(expires_delta)
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    An extension of OAuth2 authentication for FastAPI that allows retrieving the access token from an httpOnly cookie.

    This class extends the OAuth2 class provided by FastAPI to enable authentication using a Bearer token stored in
    an httpOnly cookie. It overrides the `__call__` method to retrieve the access token from the cookie and authenticate
    the user based on the Bearer scheme.

    Parameters:
        tokenUrl (str): The URL to obtain the token from. This will be used to construct the OAuth2 flow.
        scheme_name (Optional[str], optional): The name of the authentication scheme. Defaults to None.
        scopes (Optional[Dict[str, str]], optional): The dictionary of scopes for the OAuth2 flow. Defaults to None.
        auto_error (bool, optional): If set to True, the authentication will raise an HTTPException if not authenticated.
                                    If set to False, it will return None instead. Defaults to True.

    Returns:
        Optional[str]: The access token extracted from the httpOnly cookie, or None if not authenticated.

    Raises:
        HTTPException: If authentication fails and `auto_error` is set to True, it will raise an HTTPException with
                       status code 401 (UNAUTHORIZED) and the "WWW-Authenticate" header set to "Bearer".

    Example:
        # Initialize OAuth2PasswordBearerWithCookie
        oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

        # Use it in a FastAPI route
        @app.get("/protected/")
        async def protected_route(token: str = Depends(oauth2_scheme)):
            if token:
                return {"message": "Access granted!"}
            return {"message": "Access denied!"}

    Note:
        Make sure that the access token is stored in an httpOnly cookie with the name "access_token". The cookie will
        be accessed from the incoming request to authenticate the user.

    """

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        """
        Initialize the OAuth2PasswordBearerWithCookie instance.

        Args:
            tokenUrl (str): The URL to obtain the token from. This will be used to construct the OAuth2 flow.
            scheme_name (Optional[str], optional): The name of the authentication scheme. Defaults to None.
            scopes (Optional[Dict[str, str]], optional): The dictionary of scopes for the OAuth2 flow. Defaults to None.
            auto_error (bool, optional): If set to True, the authentication will raise an HTTPException if not authenticated.
                                        If set to False, it will return None instead. Defaults to True.

        """
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        """
        Override the __call__ method to authenticate the user based on the Bearer token in the httpOnly cookie.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Optional[str]: The access token extracted from the httpOnly cookie, or None if not authenticated.

        Raises:
            HTTPException: If authentication fails and `auto_error` is set to True, it will raise an HTTPException with
                           status code 401 (UNAUTHORIZED) and the "WWW-Authenticate" header set to "Bearer".

        """
        authorization: str = request.cookies.get(
            "access_token"
        )  # changed to accept access token from httpOnly Cookie

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param
