import smtplib
import email.message

def enviar_email():

    CODIGO = ''

    corpo_email = f"""
      <div style="background-color: rgb(247,247,247); text-align: center;font-family: Poppins,Helvetica,sans-serif; color:rgb(93,102,111);">
          <div style="padding-top: 10px;">
            <img src="https://processoagil.com.br/assets/media/logos/logo_processoagil.png" alt="" height="50px">
          </div>
          <div style="    padding: 10px;    background: white;    border-radius: 10px;    margin: 50px;">
            <h4 >Seu <b>código</b> de validação do email chegou! </h4>                
              <div >
                  <h1><b>{ CODIGO }</b></h1>
              </div>
            
            <br>
          </div>
          <div style="padding-bottom:10px">
            <p>Desenvolvido com carinho</p>
            <p>Pelo time da ProcessoÁgil.</p>
          </div>
      </div>
    """

    msg = email.message.Message()
    msg['Subject'] = "bote logo um escape dore nessa motocicleta rapaz vire macho "
    msg['From'] = 'sostenesj60@gmail.com'
    msg['To'] = 'sostenesj60@gmail.com'
    password = 'widydxbnjvdfxusp' 

    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')

enviar_email()