

<div align="center">
<img src="./assets/images/logo.png" width="150">
</div>
<div align="center">
  <h1 align="center">🇮🇹 ITA vs. COVID 🦠</h1>
  Un bot telegram che ti aggiorna sulla battaglia contro il Covid in Italia.
</div>

### Configurazione
Copia tutti i file `.env.sample` nei relativi `.env` con le preferenze personali.

### Avvio
Il bot utilizza [docker](https://www.docker.com/) e [docker-compose](https://docs.docker.com/compose).
```
docker-compose up --build
```

### Crediti

Il bot è stato sviluppato da [@derogab](https://github.com/derogab) e il codice sorgente è pubblicamente disponibile su Github. 

I dati mostrati sono scaricati dagli [Open Data ufficiali](https://github.com/italia/covid19-opendata-vaccini) sui vaccini in Italia. 

Fino alla [v1.0.0](#v1.0.0) i grafici sono automaticamente generati mediante il codice della [repository pubblica](https://github.com/MarcoBuster/quanto-manca) di [@MarcoBuster](https://github.com/MarcoBuster). Dalla [v2.0.0](#v2.0.0) sono invece utilizzati dei grafici differenti costruiti sulla base dei precedenti.
