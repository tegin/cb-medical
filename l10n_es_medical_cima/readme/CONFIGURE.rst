In order to configure it, we need to load all data. To do that, execute the following code in shell (it might take several hours):

.. code-block:: python
  url = "https://cima.aemps.es/cima/rest/"
  import requests
  page = 1
  presentations = requests.get("%spresentaciones" % url, params={"comerc": 1, "pagina": page}).json()
  while True:
      print("processing page %s" % page)
      for result in presentations["resultados"]:
          if "dcp" not in result:
              continue
          self.env["medical.product.product.commercial"].with_context(active_test=False)._import_cima_data(result, requests.get("%smedicamento" % url, params={"cn": result["cn"]}).json())
          env.cr.commit()
      page += 1
      presentations = requests.get("%spresentaciones" % url, params={"comerc": 1, "pagina": page}).json()
      if (presentations["totalFilas"] < presentations["pagina"] * presentations["tamanioPagina"]):
          break
