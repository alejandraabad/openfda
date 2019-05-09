import http.server
import http.client
import json
import socketserver
IP="127.0.0.1"
PORT = 8000


class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    URL = "api.fda.gov"
    LABEL = "/drug/label.json"
    DRUG = '&search=active_ingredient:'
    COMPANY = '&search=openfda.manufacturer_name:'


    def main_app(self):
        html = """
            <html>
                <head>
                    <title>Aplicacion OpenFDA</title>
                </head>
                <body align=center style='background-color: CDA7DF'>
                    <h1>Bienvenid@ a la pagina principal del programa </h1>
                    <br>
                    <p>Introduzca el componente activo:</p>
                    <form method="get" action="searchDrug">
                        <input type = "text" name="drug"></input>
                        <input type = "submit" value="Buscar medicamentos">
                        </input>
                    </form>
                    <br>
                    <br>
                    <form method="get" action="listDrugs">
                        <input type = "submit" value="Lista de medicamentos">
                        </input>
                        Limite: <input type="text" name="limit">
                        </input>
                    </form>
                    <br>
                    <br>
                    <p>Introduzca el nombre de la empresa:</p>
                    <form method="get" action="searchCompany">
                        <input type = "text" name="company"></input>
                        <input type = "submit" value="Buscar empresas">
                        </input>
                       
                    </form>
                    <br>
                    <br>
                    <form method="get" action="listCompanies">
                        <input type = "submit" value="Lista de empresas">
                        </input>
                        Limite: <input type="text" name="limit">
                        </input>
                    </form>
                    <br>
                    <br>
                    <form method="get" action="listWarnings">
                        <input type = "submit" value="Lista de advertencias">
                        </input>
                        Limite: <input type="text" name="limit">
                        </input>
                    </form>
                    <br>
                    <br>
                    <p> Practica hecha por Alejandra Abad Gonzalez </p>
                    <p> Grado en Ingenieria Biomedica - URJC </p>
                </body>
            </html>
                """
        return html

    def web(self, lista):
        lista_html = """
                                        <html>
                                            <head>
                                                <title>Aplicacion OpenFDA</title>
                                            </head>
                                            <body style='background-color: A7DFAF'>
                                                <h1> La informacion solicitada es: </h1>
                                                <br>
                                                <ul>
                                    """
        for item in lista:
            lista_html += "<li>" + item + "</li>"

        lista_html += """
                                                </ul>
                                                <a href="/">Volver</a>
                                            </body>
                                        </html>
                                    """

        return lista_html

    def web2(self,text):
        mensaje = """
                                        <html>
                                            <head>
                                                <title>ERROR 404</title>
                                            </head>
                                            <body style='background-color: 9c1325'> """
        mensaje += "<p>"+ text + "</p>"
                                    
        mensaje += """ 
                                                <a href="/">Volver</a>
                                            </body>
                                        </html>
                                    """

        return mensaje

    def dame_resultados(self, limit=10):
        conexion = http.client.HTTPSConnection(self.URL)
        #envía la solicitud
        conexion.request("GET", self.LABEL + "?limit=" + str(limit))
        print (self.LABEL + "?limit=" + str(limit))
        #recibe la respuesta del servidor
        respuesta = conexion.getresponse()
        #lee el json y lo transforma en una cadena
        label = respuesta.read().decode("utf8")
        conexion.close()
        #procesa el contenido del json
        info = json.loads(label)
        resultados = info['results']
        return resultados


    def do_GET(self):
        # Para separar los parametros
        lista_recurso = self.path.split("?")
        if len(lista_recurso) > 1:  
            parametros = lista_recurso[1]        
            
        else:
            parametros = ""
        if parametros:
            print("Hay parametros")
        else:
            print("Sin parametros")

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.main_app()
            self.wfile.write(bytes(html, "utf8"))

        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit=self.path.split('=')[1]
            if limit == "":
                limit=22
            try:
                lista_medicamentos = []
                resultados = self.dame_resultados(limit)
                #creamos una lista con los nombres de los medicamentos
                for resultado in resultados:
                    if 'generic_name' in resultado['openfda']:
                        lista_medicamentos.append(resultado['openfda']['generic_name'][0])
                    else:
                        lista_medicamentos.append('Se desconoce el nombre del medicamento')
                limit = str(limit)
                resultado_html = self.web(lista_medicamentos)
                self.wfile.write(bytes(resultado_html, "utf8"))

            except KeyError:
                resultado_html=self.web2("Numero de medicamentos solicitado mayor del existente")
                self.wfile.write(bytes(resultado_html, "utf8"))


        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit=self.path.split('=')[1]
            if limit == "":
                limit=10
            try:
                lista_empresas = []
                resultados = self.dame_resultados(limit)
                #creamos una lista con los nombres de las empresas
                for resultado in resultados:
                    if 'manufacturer_name' in resultado['openfda']:
                        lista_empresas.append(resultado['openfda']['manufacturer_name'][0])
                    else:
                        lista_empresas.append('Desconocida')
                resultado_html = self.web(lista_empresas)
                self.wfile.write(bytes(resultado_html, "utf8"))
            except KeyError:
                resultado_html=self.web2("Numero de empresas solicitado mayor del existente")
                self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'listWarnings' in self.path:
            # listWarnings te devuelve las advertencias de los medicamentos.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit=self.path.split('=')[1]
            if limit == "":
                limit=10
            try:
                lista_advertencias = []
                resultados = self.dame_resultados(limit)
                for resultado in resultados:
                    if 'warnings' in resultado:
                        lista_advertencias.append(resultado['warnings'][0])
                    else:
                        lista_advertencias.append('Se desconoce las advertencias')
                resultado_html = self.web(lista_advertencias)
                self.wfile.write(bytes(resultado_html, "utf8"))
            except KeyError:
                resultado_html=self.web2("Numero de advertencias solicitado mayor del existente")
                self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            componente_activo = self.path.split('=')[1]
            limit=10
            
            try:
                if componente_activo == "":
                    resultado_html=self.web2("Debe introducir una respuesta")
                    self.wfile.write(bytes(resultado_html, "utf8"))
                    print(componente_activo)
                else:
                    lista_componentes = []
                    conexion = http.client.HTTPSConnection(self.URL)
                    conexion.request("GET",self.LABEL + "?limit=" + str(limit) + self.DRUG + componente_activo)
                    respuesta = conexion.getresponse()
                    label1 = respuesta.read().decode("utf8")
                    info1 = json.loads(label1)
                    buscador_componente = info1['results']
                    for resultado in buscador_componente:
                        if 'generic_name' in resultado['openfda']:
                            lista_componentes.append(resultado['openfda']['generic_name'][0])
                        else:
                            lista_componentes.append('Se desconoce el componente activo del medicamento')
                    resultado_html = self.web(lista_componentes)
                    self.wfile.write(bytes(resultado_html, "utf8"))
            except KeyError:
                resultado_html=self.web2("Medicamento no encontrado")
                self.wfile.write(bytes(resultado_html, "utf8"))
                self.send_response(404)

               
                
              
        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit=10
            empresa = self.path.split('=')[1]
            try:
                if empresa == "":
                    resultado_html=self.web2("Debe introducir una respuesta")
                    self.wfile.write(bytes(resultado_html, "utf8"))
                else:
                    lista_empresa = []
                    conexion = http.client.HTTPSConnection(self.URL)
                    conexion.request("GET", self.LABEL + "?limit=" + str(limit) + self.COMPANY + empresa)
                    respuesta = conexion.getresponse()
                    label2 = respuesta.read().decode("utf8")
                    info2 = json.loads(label2)
                    buscador_empresa = info2['results']
                    for resultado2 in buscador_empresa:
                        if 'manufacturer_name' in resultado2['openfda']:
                    
                            lista_empresa.append(resultado2['openfda']['manufacturer_name'][0])
                        else:
                            lista_empresa.append("No se conoce el nombre")
                    resultado_html = self.web(lista_empresa)
                    self.wfile.write(bytes(resultado_html, "utf8"))
            except KeyError:
                resultado_html=self.web2("Empresa no encontrada")
                self.wfile.write(bytes(resultado_html, "utf8"))


        elif 'redirect' in self.path:  # Te dirige hacia la pagina principal
            self.send_response(301)
            self.send_header('Location', 'http://localhost:' + str(PORT))
            self.end_headers()
        elif 'secret' in self.path: #Te pide datos para acceder a sitios privados
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')  #le envias la cabecera
            self.end_headers()
        else:
            self.send_response(404) #error 404
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("No encuentro ese recurso '{}'.".format(self.path).encode())
        return


socketserver.TCPServer.allow_reuse_address = True
Handler = testHTTPRequestHandler


httpd = socketserver.TCPServer(("", PORT), Handler)
print("Sirviendo en el puerto:", PORT)
try:
    httpd.serve_forever()


except KeyboardInterrupt:
    print("El usuario ha interrumpido el servidor en el puerto:", PORT)
    print("Reanudelo de nuevo")
    print("Servidor parado")
