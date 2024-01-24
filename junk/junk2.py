html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;700&display=swap"
      rel="stylesheet"
    />
  </head>
  <body
    style="
      text-align: center;

      background-color: #eaf0f3;
      font-family: 'Barlow', serif;
      margin: 100px 0;
    "
  >
    <div class="mail" style="text-align: center">
      <header>
        <div class="header" style="padding-bottom: 55px; margin: auto">
      
          <div
            class="greet"
            style="
              box-sizing: border-box;
              font-size: 52px;
              letter-spacing: 0;
              line-height: 62px;
              text-align: center;
              width: 60%;
              margin: auto;
            "
            width="60%"
          >
            <p style="margin: 0; padding: 0">
              Hi <span style="font-weight: bold">{existing_user[1]}</span>,
            </p>
            <p style="margin: 0; padding: 0">
              Thank you for registering with [Your Service]. To complete your registration, please click the link below to verify your email address.
            </p>
          </div>
        </div>
      </header>

      <section
        class="main-content"
        style="
          background-color: white;
          border-radius: 6px;
          font-size: 24px;
          padding: 63px, 267px, 146px, 266px;
          text-align: center;
          width: 60%;
          min-height: 350px;
          margin: auto;
        "
      >
        <div style="display: inline-block; margin: auto">
          <div
            class="content"
            style="
              margin: 20px;
              padding: 10px;
              border-bottom: 1px solid #e5e5e5;
              max-width: 579px;
              
            "
          >
            <p style="font-weight: bold;">OTP : {otp}</p>
            <p> This code will expire in 5 minutes. If you did not initiate this request, please disregard this email.
            </p>
          </div>
          <p style="margin: 0; padding: 0; max-width: 579px">
            You can set your password by clicking the link below:
            <a href="[Your Password Setup Link]">Set Password</a>
          </p>
          <a
            class="button"
            href=""
            style="
              background-color: #3490ec;
              border-radius: 60px;
              color: white;
              margin: auto;
              padding: 20px 100px;
              display: block;
              width: 30%;
              margin-top: 40px;
              margin-bottom: 40px;
            "
            >Get started</a
          >
        </div>
      </section>

      <section
        class="app-advt"
        style="
          background-color: white;
          border-radius: 6px;
          margin: auto;
          margin-top: 40px;
          padding: 40px 0;
          text-align: center;
          width: 60%;
          min-height: 350px;
        "
      >
        <h2 style="font-size: 42.21px">Get the [Your Service] app!</h2>
        <p style="margin: 0; padding: 0; font-size: 24px; max-width: 669px; margin: auto;">
          Get the most out of [Your Service] by installing our mobile app. You can
          log in using your existing email address and password.
        </p>
      </section>

      <footer style="margin-top: 50px;">
        <p>Copyright  &copy; 2023</p>
        <p style="font-weight: bold; "><span>PortfolioOne</span></p>
        <p>PortfolioOne tagline</p>
      </footer>
    </div>
  </body>
</html>
"""
