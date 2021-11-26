
<h1 align="center">:it: ITA vs. COVID :microbe:</h1>
<p align="center">
    <img src="./assets/images/logo.png" alt="header" width="150px">
</p>
<h3 align="center">Un bot telegram che ti aggiorna sulla battaglia contro il Covid in Italia</h3>
<p align="center">
    <a href="https://hub.docker.com/r/derogab/itavscovidbot">
        <img src="https://img.shields.io/docker/pulls/derogab/itavscovidbot?label=Downloads&logo=docker" alt="Docker Pulls">
    </a>
    <a href="https://github.com/derogab/itavscovidbot/actions/workflows/docker-publish.yml">
        <img src="https://github.com/derogab/itavscovidbot/actions/workflows/docker-publish.yml/badge.svg" alt="Build & Push Docker Image">
    </a>
</p>


## Configurazione
Copia tutti i file `.env.sample` nei relativi `.env` con le preferenze personali.

## Avvio
Il bot utilizza [docker](https://www.docker.com/) e [docker-compose](https://docs.docker.com/compose).
```
docker-compose up --build
```

## Crediti

Il bot è stato sviluppato da [@derogab](https://github.com/derogab) e il codice sorgente è pubblicamente disponibile su Github. 

I dati mostrati sono scaricati dagli [Open Data ufficiali](https://github.com/italia/covid19-opendata-vaccini) sui vaccini in Italia. 

Fino alla [v1.0.0](https://github.com/derogab/ITAvsCOVIDbot/releases/tag/v1.0.0) i grafici sono automaticamente generati mediante il codice della [repository pubblica](https://github.com/MarcoBuster/quanto-manca) di [@MarcoBuster](https://github.com/MarcoBuster). La [v2.0.0](https://github.com/derogab/ITAvsCOVIDbot/releases/tag/v2.0.0) introduce invece un aggiornamento di questi grafici.
