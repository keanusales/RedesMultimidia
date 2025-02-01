## Forma de executar o programa:

**Cliente**
```bash
$ python3 ClientLauncher.py <endereço|ex:localhost> <porta|ex:9999> <portaRTP|ex:5004> <arquivo|ex:movie.Mjpeg>
```

**Servidor**
```bash
$ python3 Server.py <porta|ex:9999>
```

O servidor busca o arquivo de mídia no diretório "resources" onde está o codigo fonte.
O caminho é relativo ao diretório de trabalho.
Então se você executar o script do servidor de fora da pasta onde o mesmo se encontra,
o arquivo não será encontrado.
Em IDEs como o PyCharm, você pode configurar o diretório de trabalho na configuração de execução do script.