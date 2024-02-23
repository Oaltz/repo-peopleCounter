<h1 align="center">People Counter</h1>

###

<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pycharm/pycharm-original.svg" height="40" alt="pycharm logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/anaconda/anaconda-original.svg" height="40" alt="anaconda logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="python logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/opencv/opencv-original.svg" height="40" alt="opencv logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" height="40" alt="pandas logo"  />
</div>

<h2>Índice 📌</h2>

<p>
    <ul style="list-style-type: none;">
        <a href="#resumo"><li>Resumo</li></a>
        <a href="#tecnico"><li>Técnico</li></a>
            <ul style="list-style-type: none;">
                <a href="#opencv"><li>OpenCV</li></a>
                <a href="#pandas"><li>Pandas</li></a>
            </ul>
        <a href="#finalidade"><li>Finalidade</li></a>
    </ul>
</p>

<hr>

<h2 id="resumo">💡 Resumo</h2>

<p>Este algoritmo é capaz de realizar a contagem de pessoas que estão subindo e descendo, descartando pessoas que estão usando roupas da cor laranja, e ao final de cada hora salva os registros coletados em um arquivo CSV para uma futura análise.</p>

###

<div align="center">
  <img height="200" src="Examples/example.gif"  />
</div>

<hr>

<h2 id="tecnico">💻 Técnico</h2>

<h3 id="opencv">🤖 OpenCV (cv2):</h3>

<p>O OpenCV é usado para processamento de vídeo e imagem. Ele fornece funções para ler frames de vídeo, aplicar técnicas de subtração de fundo, detecção de contornos, análise de cores, desenho de linhas e formas, entre outros. No código, o OpenCV esta sendo utilizado para realizar a detecção de objetos em movimento, contagem de pessoas atravessando uma linha e exibição dos resultados visuais em tempo real.</p>

###

<h3 id="pandas">🐼 Pandas (pd):</h3>

<p>O Pandas é utilizado para armazenar e manipular os resultados das detecções em um formato de tabelas. Ele facilita a organização dos dados, permitindo a sua posterior análise e exportação para um arquivo CSV. No código, o Pandas é utilizado para armazenar os resultados de detecção, incluindo informações como o 'timestamp', o total de pessoas detectadas, e quantas estão subindo ou descendo, facilitando a análise posterior desses dados.</p>

<hr>

<h2 id="finalidade">📋 Finalidade</h2>

<p>Por finalidade o projeto tem como foco a implementação em lojas em câmeras de segurança que fornecem uma análise em tempo real através de uma conexão RTSP, e dessa forma ter um controle entre Clientes que entram em loja x Clientes que compram em loja, e assim poder realizar diversos tipos de análises de dados para otimização de vários aspectos.</p>