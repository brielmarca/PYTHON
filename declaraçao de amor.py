from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Minha Declaração de Amor</title>
        <style>
            body {
                background-color: #ffe6e6;
                font-family: Arial, sans-serif;
                text-align: center;
                padding-top: 50px;
            }
            .container {
                max-width: 600px;
                margin: auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #ff4d4d;
            }
            p {
                font-size: 18px;
                color: #333;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                margin-top: 20px;
                cursor: pointer;
                border: none;
                background-color: #ff4d4d;
                color: white;
                border-radius: 5px;
            }
            @keyframes explode {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.5); opacity: 1; }
                100% { transform: scale(2); opacity: 0; }
            }
            #explosionMessage h2 {
                color: #ff4d4d;
                animation: fadeIn 1s forwards;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Princesa da minha vida</h1>
            <p>Quero declarar o quanto te amo, minha linda. Você é o sol da minha vida e a razão do meu sorriso. Cada dia ao seu lado é um presente precioso.</p>
            <button id="btnExplode">Clique aqui</button>
            <div id="explosionMessage" style="display: none;">
                <h2>Você é a melhor namorada do mundo!</h2>
            </div>
        </div>
        <script>
            document.getElementById('btnExplode').addEventListener('click', function(){
                var btn = this;
                btn.style.animation = "explode 0.6s forwards";
                setTimeout(function(){
                    btn.style.display = 'none';
                    document.getElementById('explosionMessage').style.display = 'block';
                }, 600);
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    print("Inicie o Ngrok manualmente com: ngrok http 5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
