#!/usr/bin/env python


# In[1]:


import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.express as px
import streamlit as st
from plotly import __version__
print("Plotly version: ",__version__)
import os
import math

st.set_page_config(
    page_title="ComputeForm",
    layout="wide",
    initial_sidebar_state="expanded")


st.title('Form Calcolo Tempi Lavorazione')

#variabili utente da configurare in base a riscontri teorici o effettivi
costante_tornitura = 5 #tempo da considerare per preparazione tornitura (in questo modo si conteggia un tempo anche sulle viti piccole dove 
                       # la q. di materiale asportato è minima
tempo_asportazione = 0.0001 #tempo asportazione per viti per ogni mm2 di materiale asportato
tempo_asportazioneC = 0.0001 #tempo asportazione per chiocciole
tempo_lav_accessorie = 2 #lavorazioni che vengono eseguite sempre al tornio con stessa piazzatura iniziale
tempo_lav_accessorieC = 2 #cs. per chiocciole
tempo_altrelav = 4 #lavorazioni che vengono eseguite su altri macchinari con una piazzatura diversa
tempo_altrelavC = 4# cs. per chiocciole
tempo_piazzaturaU = 30 #tempo medio per ogni piazzatura macchine accessori
tempo_piazzaturaMann = 90 #tempo piazzatura mannaioni (per filetttatura chiocciole)
tempo_piazzaturaFil = 150 #tempo piazzatura filettatore (per filetttatura viti a disegno)

codice_articolo = st.sidebar.text_input("codice articolo da lavorare")
pezzi_ottimali = st.sidebar.number_input("n° pezzi ottimale in lavorazione", value = 30, step = 1)
#il numero di pezzi ottimali serve per calcolare un certo decremento dei tempi tramite la funzione apposita

#calcolo variabili utente in base a tipologia materiali e caratteristiche pezzo (viti)
tipo_pezzo = st.sidebar.radio("scegliere tipo pezzo da realizzare",('Viti', 'Chiocciole', 'Altro'))

if tipo_pezzo =='Viti':
    materiale = st.sidebar.radio("materiale", ('avp-r80', 'r100', 'inox'))
    if materiale == 'avp-r80':
        tempo_asportazioneU = tempo_asportazione
        tempo_lav_accessorieU = tempo_lav_accessorie
        tempo_altrelavU = tempo_altrelav
    else:
        if materiale == 'r100':
            tempo_asportazioneU = tempo_asportazione*1.5
            tempo_lav_accessorieU = tempo_lav_accessorie*1.25
            tempo_altrelavU = tempo_altrelav*1.25
        else:
            tempo_asportazioneU = tempo_asportazione*2  
            tempo_lav_accessorieU = tempo_lav_accessorie*1.5
            tempo_altrelavU = tempo_altrelav*1.5
            

    barra_lunga = st.sidebar.checkbox("barra lunga")
    if barra_lunga == True:
        tempo_asportazioneU=tempo_asportazioneU*1.3

    st.sidebar.text("tempo U. asportazione Viti = " + str(tempo_asportazioneU))
    st.sidebar.text("tempo U. lav. accessorie Viti = " + str(tempo_lav_accessorieU))
    st.sidebar.text("tempo U. altre lav. Viti = " + str(tempo_altrelavU))

    st.subheader("latoA")


    col1, col2, = st.columns(2)
    diam_partenzaA = col1.number_input('inserire diametro di partenza latoA', value = 0, step = 1)
    
    n_diametriA = col2.number_input('inserire n° di diametri da ricavare in tornitura latoA', value = 0, step = 1)
    calcolo_asportazione_listA = []

    #loop creazione box per diametri e lunghezze
    for i in range(n_diametriA):
        with st.expander(f"Diametro (A) {i+1}"):
            diameter = col1.number_input("Diametro", key=f"diameterA_{i}")
            length = col2.number_input("Lunghezza", key=f"lengthA_{i}")
            calcolo_asportazione = ((math.pi * ((diam_partenzaA/2) ** 2) * length )-(math.pi * ((diameter/2) ** 2) * length ))
            calcolo_asportazione_listA.append(calcolo_asportazione)  #aggiunti valori a lista

    totale_calcolo_asportazioneA = int(sum(calcolo_asportazione_listA))
    if n_diametriA >0:
        tempo_tornituraA = costante_tornitura+round(tempo_asportazioneU*totale_calcolo_asportazioneA)
    else:
        tempo_tornituraA = 0
    st.text("asportazione mm^2 " + str(totale_calcolo_asportazioneA))
    st.text("tempo solo tornitura lato A " + str(tempo_tornituraA))
    
    #lavorazioni accessorie tornitura
    tempo_lav_accessorieA = tempo_lav_accessorieU+tempo_lav_accessorieU*int(diam_partenzaA/40)
    altre_lavTornA = st.multiselect('indicare lavorazioni accessorie tornio latoA', 
                                ['maschiatura', 'spianatura+smussi','filettatura filiera', 'filettatura man.',
                                 'foratura', 'foratura profonda', 'alesatura', 'tornitura con contropunta',
                                 'finitura molto precisa', 'ripulitura', 'seeger1', 'seeger2','tornitura gola/scanalatura','brocciatura esagono','altro'])
    n_lavTornA = len(altre_lavTornA)
    totale_tempo_lav_accessorieA = (n_lavTornA*tempo_lav_accessorieA)

    totaleTornituraA = (tempo_tornituraA+totale_tempo_lav_accessorieA)

    st.text("n° lavorazioni tornio accessorie lato A = " + str(n_lavTornA))
    st.text("minuti lavorazioni accessorie tornitura lato A min " + str(totale_tempo_lav_accessorieA))
    st.text("totale tempo lavorazione tornitura lato A  min " + str(totaleTornituraA))    

    #altre lavorazioni
    altre_lavA = st.multiselect('indicare lavorazioni su altre macchine latoA', 
                                ['fresatura', 'chiavetta', 'foro trasversale',
                                 'altro'])
    n_lavA = len(altre_lavA)
    tempo_altrelavA=tempo_altrelavU+tempo_altrelavU*(diam_partenzaA/40)
    totale_tempo_altrelavA = int(n_lavA*tempo_altrelavA)
    totaleA = int(tempo_tornituraA+totale_tempo_lav_accessorieA+totale_tempo_altrelavA)
    st.text("n° altre lavorazioni lato A = " + str(n_lavA))
    st.text("totale tempo altre lavorazioni lato A min " + str(totale_tempo_altrelavA))   
    st.text("totale tempo lavorazione lato A min " + str(totaleA))   



    st.subheader("latoB")
    col3, col4, = st.columns(2)
    diam_partenzaB = col3.number_input('inserire diametro di partenza latoB', value = 0, step = 1)
    n_diametriB = col4.number_input('inserire n° di diametri da ricavare in tornitura latoB', value = 0, step = 1)
    calcolo_asportazione_listB = []

    #loop creazione box per diametri e lunghezze
    for i in range(n_diametriB):
        with st.expander(f"Diametro (B) {i+1}"):
            diameter = col3.number_input("Diametro", key=f"diameterB_{i}")
            length = col4.number_input("Lunghezza", key=f"lengthB_{i}")
            calcolo_asportazione = ((math.pi * ((diam_partenzaB/2) ** 2) * length )-(math.pi * ((diameter/2) ** 2) * length ))
            calcolo_asportazione_listB.append(calcolo_asportazione)  #aggiunti valori a lista 

    totale_calcolo_asportazioneB = int(sum(calcolo_asportazione_listB))
    if n_diametriB >0:
        tempo_tornituraB = costante_tornitura+round(tempo_asportazioneU*totale_calcolo_asportazioneB)
    else:
        tempo_tornituraB = 0
    st.text("asportazione mm^2 " + str(totale_calcolo_asportazioneB))
    st.text("tempo solo tornitura lato B " + str(tempo_tornituraB))

    #lavorazioni accessorie tornitura
    tempo_lav_accessorieB = tempo_lav_accessorieU+tempo_lav_accessorieU*int(diam_partenzaB/40)
    altre_lavTornB = st.multiselect('indicare lavorazioni accessorie tornio latoB', 
                                ['maschiatura', 'spianatura+smussi','filettatura filiera', 'filettatura man.',
                                 'foratura', 'foratura profonda', 'alesatura', 'tornitura con contropunta',
                                 'finitura molto precisa', 'ripulitura', 'seeger1', 'seeger2','brocciatura esagono','altro'])
    n_lavTornB = len(altre_lavTornB)
    totale_tempo_lav_accessorieB = (n_lavTornB*tempo_lav_accessorieB)

    totaleTornituraB = (tempo_tornituraB+totale_tempo_lav_accessorieB)

    st.text("n° lavorazioni tornio accessorie lato B = " + str(n_lavTornB))
    st.text("minuti lavorazioni accessorie tornitura lato B " + str(totale_tempo_lav_accessorieB))
    st.text("totale tempo lavorazione tornitura lato B " + str(totaleTornituraB))    


    altre_lavB = st.multiselect('indicare lavorazioni su altre macchine latoB', 
                                ['fresatura', 'chiavetta', 'foro trasversale',
                                 'altro'])
    n_lavB = len(altre_lavB)
    tempo_altrelavB=tempo_altrelavU+tempo_altrelavU*(diam_partenzaB/40)
    totale_tempo_altrelavB = int(n_lavB*(tempo_altrelavB))
    totaleB = int(tempo_tornituraB+totale_tempo_lav_accessorieB+totale_tempo_altrelavB)
    st.text("n° altre lavorazioni lato B = " + str(n_lavB))
    st.text("totale tempo altre lavorazioni lato B min " + str(totale_tempo_altrelavB)) 
    st.text("totale tempo lavorazione lato B min " + str(totaleB))   

    #riepilogo valori per pezzo singolo
    st.header("Riepilogo")
    col5, col6, = st.columns(2)
    tempo_lavorazioni_aggiuntive=col5.number_input(
        "minuti lavorazioni aggiuntive da conteggiare separatamente (es. maschiatura/filettatura TR, ripulitura alle spazzole etc..) ", 
         value = 0, step = 1)
    n_piazzatura=col5.number_input("n° macchine (piazzature tornio/trapani/fresa ecc..) utilizzate = ", value = 0, step = 1)
    n_piazzaturaMann=col5.number_input("n° piazzature mannaioni = ", value = 0, step = 1)
    n_piazzaturaFil=col5.number_input("n° piazzature filettatori = ", value = 0, step = 1)
    tempo_piazzatura = n_piazzatura*tempo_piazzaturaU + n_piazzaturaMann*tempo_piazzaturaMann +  n_piazzaturaFil*tempo_piazzaturaFil 
    tempo_tornitura = totaleTornituraA+totaleTornituraB
    tempo_altre_lav = totale_tempo_altrelavA+totale_tempo_altrelavB
    tempo_totale_senza_piazz = totaleA+totaleB+tempo_lavorazioni_aggiuntive
    tempo_totale_con_piazz = totaleA+totaleB+tempo_piazzatura+tempo_lavorazioni_aggiuntive

    st.text("totale tempo tornitura min " + str(tempo_tornitura))
    st.text("totale tempo altre lavorazioni min " + str(tempo_altre_lav))
    st.text("totale tempo lavorazioni aggiuntive min " + str(tempo_lavorazioni_aggiuntive))
    st.text("totale tempo globale lavorazioni (escluso piazzatura) min " + str(tempo_totale_senza_piazz))
    st.text("totale piazzature min " + str(tempo_piazzatura))
    st.text("totale tempo globale lavorazioni con piazzatura min " + str(tempo_totale_con_piazz))

if tipo_pezzo =='Chiocciole':
    #calcolo variabili utente in base a tipologia materiali e caratteristiche pezzo (chiocciole)
    materiale = st.sidebar.radio("materiale", ('bronzo-ottone-avp', 'brall', 'mat_plastico'))
    if materiale == 'bronzo-ottone-avp':
        tempo_asportazioneU = tempo_asportazione
        tempo_preforoU = tempo_asportazione
        tempo_lav_accessorieU = tempo_lav_accessorieC
        tempo_altrelavU = tempo_altrelavC
    else:
        if materiale == 'brall':
            tempo_asportazioneU = tempo_asportazioneC*1.5
            tempo_preforoU = tempo_asportazione*1.5
            tempo_lav_accessorieU = tempo_lav_accessorieC*1.5
            tempo_altrelavU = tempo_altrelavC*1.5
        else:
            tempo_asportazioneU = tempo_asportazione*0.8  
            tempo_preforoU = tempo_asportazione*1.5
            tempo_lav_accessorieU = tempo_lav_accessorieC*0.8
            tempo_altrelavU = tempo_altrelavC*0.8

    st.sidebar.text("tempo U. asportazione Chiocciole = " + str(tempo_asportazioneU))
    st.sidebar.text("tempo U. lav. accessorie Chiocciole = " + str(tempo_lav_accessorieU))
    st.sidebar.text("tempo U. altre lav. Chiocciole = " + str(tempo_altrelavU))

    st.subheader("Preforo")
    col5, col6, = st.columns(2)
    diam_preforo = col5.number_input('inserire diametro punta preforo', value = 0, step = 1)
    lpreforo = col6.number_input('inserire lunghezza da preforare', value = 0, step = 1)
    asportazione_preforo = ((math.pi * ((diam_preforo/2) ** 2) * lpreforo ))
    if diam_preforo !=0:
        tempo_preforo = round(tempo_preforoU*asportazione_preforo)
    else:
        tempo_preforo = 0
    st.text("asportazione mm^2 preforo" + str(asportazione_preforo))
    st.text("tempo preforo " + str(tempo_preforo))
    
    
    st.subheader("Esterno")
    col1, col2, = st.columns(2)
    diam_partenzaEC = col1.number_input('inserire diametro di partenza esterno chiocciola', value = 0, step = 1)
    
    n_diametriEC = col2.number_input('inserire n° di diametri da ricavare in tornitura esterno chiocciola', value = 0, step = 1)
    calcolo_asportazione_EC = []

    #loop creazione box per diametri e lunghezze
    for i in range(n_diametriEC):
        with st.expander(f"Diametro esterno chiocciola (A) {i+1}"):
            diameter = col1.number_input("Diametro", key=f"diameterEC_{i}")
            length = col2.number_input("Lunghezza", key=f"lengthEC_{i}")
            calcolo_asportazione = ((math.pi * ((diam_partenzaEC/2) ** 2) * length )-(math.pi * ((diameter/2) ** 2) * length ))
            calcolo_asportazione_EC.append(calcolo_asportazione)  #aggiunti valori a lista

    totale_calcolo_asportazione_EC = int(sum(calcolo_asportazione_EC))
    if n_diametriEC >0:
        tempo_tornitura_EC = costante_tornitura+round(tempo_asportazioneU*totale_calcolo_asportazione_EC)
    else:
        tempo_tornitura_EC = 0
    st.text("asportazione mm^2 " + str(totale_calcolo_asportazione_EC))
    st.text("tempo solo tornitura lato A min " + str(tempo_tornitura_EC))
    
    #lavorazioni accessorie tornitura
    tempo_lav_accessorie_EC = tempo_lav_accessorieU+tempo_lav_accessorieU*int(diam_partenzaEC/60)
    altre_lavTornEC = st.multiselect('indicare lavorazioni accessorie esterno chiocciola', 
                                ['spianatura+smussi', 'doppia spianatura+smussi','spianatura+smussi flangia', 'filettatura filiera', 'filettatura man.',
                                 'finitura molto precisa', 'gola su esterno','ripulitura', 'disangolatura', 'altro'])
    n_lavTornEC = len(altre_lavTornEC)
    totale_tempo_lav_accessorieEC = (n_lavTornEC*tempo_lav_accessorie_EC)

    totaleTornituraEC = (tempo_tornitura_EC+totale_tempo_lav_accessorieEC)

    st.text("n° lavorazioni tornio accessorie esterno chiocciola = " + str(n_lavTornEC))
    st.text("minuti lavorazioni accessorie tornitura esterno chiocciola " + str(totale_tempo_lav_accessorieEC))
    st.text("totale tempo lavorazione tornitura esterno chiocciola min " + str(totaleTornituraEC))    

    #altre lavorazioni
    altre_lavEC = st.multiselect('indicare lavorazioni su altre macchine esterno chiocciola', 
                                ['fresatura', 'foratura', 'maschiatura fori', 'alesatura fori', 'fresatura flangia', 'foratura flangia', 'incassatura flangia', 
                                 'altre lavorazioni fori flangia', 'chiavetta esterna', 'foratura trasversale',
                                 'foro ingrassatore',  'altro'])
    n_lavEC = len(altre_lavEC)
    if n_lavEC >1:
        tempo_altrelavEC=tempo_altrelavU+(tempo_altrelavU*(diam_partenzaEC/60)/2)
    else:
        tempo_altrelavEC=tempo_altrelavU+(tempo_altrelavU*(diam_partenzaEC/60))
    totale_tempo_altrelavEC = int(n_lavEC*tempo_altrelavEC)
    totaleEC = int(tempo_tornitura_EC+totale_tempo_lav_accessorieEC+totale_tempo_altrelavEC)
    st.text("n° altre lavorazioni esterno chiocciola = " + str(n_lavEC))
    st.text("totale tempo altre lavorazioni esterno chiocciola min " + str(totale_tempo_altrelavEC))   
    st.text("totale tempo lavorazione esterno chiocciola min " + str(totaleEC)) 

    st.subheader("Interno")
    col3, col4, = st.columns(2)
    diam_partenzaIC = col3.number_input('inserire diametro di partenza interno chiocciola (0 = pieno)', value = 0, step = 1)
    
    n_diametriIC = col4.number_input('inserire n° di diametri da ricavare in tornitura interno chiocciola', value = 0, step = 1)
    calcolo_asportazione_IC = []

    #loop creazione box per diametri e lunghezze
    for i in range(n_diametriIC):
        with st.expander(f"Diametro interno chiocciola (A) {i+1}"):
            diameter = col3.number_input("Diametro", key=f"diameterIC_{i}")
            length = col4.number_input("Lunghezza", key=f"lengthIC_{i}")
            calcolo_asportazione = ((math.pi * ((diameter/2) ** 2) * length )-(math.pi * ((diam_partenzaIC/2) ** 2) * length ))
            calcolo_asportazione_IC.append(calcolo_asportazione)  #aggiunti valori a lista

    totale_calcolo_asportazione_IC = int(sum(calcolo_asportazione_IC))
    if n_diametriIC >0:
        tempo_tornitura_IC = costante_tornitura+round(tempo_asportazioneU*totale_calcolo_asportazione_IC)
    else:
        tempo_tornitura_IC = 0
    st.text("asportazione mm^2 " + str(totale_calcolo_asportazione_IC))
    st.text("tempo solo tornitura interno chiocciola " + str(tempo_tornitura_IC))
    
    #lavorazioni accessorie tornitura
    tempo_lav_accessorie_IC = tempo_lav_accessorieU+tempo_lav_accessorieU*int(diam_partenzaEC/60)#occorre considerare sempre esterno                                                                                                          #chiocciola
    altre_lavTornIC = st.multiselect('indicare lavorazioni accessorie interno chiocciola', 
                                ['maschiatura','foro di punta', 'smussi interno', 
                                 'scarico filettatura','gola interna', 'altro'])
    n_lavTornIC = len(altre_lavTornIC)
    totale_tempo_lav_accessorieIC = (n_lavTornIC*tempo_lav_accessorie_IC)

    totaleTornituraIC = (tempo_tornitura_IC+totale_tempo_lav_accessorieIC)

    st.text("n° lavorazioni tornio accessorie interno chiocciola = " + str(n_lavTornIC))
    st.text("minuti lavorazioni accessorie tornitura interno chiocciola " + str(totale_tempo_lav_accessorieIC))
    st.text("totale tempo lavorazione tornitura interno chiocciola min " + str(totaleTornituraIC))    

    #altre lavorazioni
    altre_lavIC = st.multiselect('indicare lavorazioni su altre macchine interno chiocciola', 
                                ['chiavetta interna',
                                 'altro'])
    n_lavIC = len(altre_lavIC)
    tempo_altrelavIC=tempo_altrelavU+tempo_altrelavU*(diam_partenzaIC/60)
    totale_tempo_altrelavIC = int(n_lavIC*tempo_altrelavIC)
    totaleIC = int(tempo_tornitura_IC+totale_tempo_lav_accessorieIC+totale_tempo_altrelavIC)
    st.text("n° altre lavorazioni interno chiocciola = " + str(n_lavIC))
    st.text("totale tempo altre lavorazioni interno chiocciola min " + str(totale_tempo_altrelavIC))   
    st.text("totale tempo lavorazione sterno chiocciola min " + str(totaleIC))
    
    #riepilogo valori per pezzo singolo
    st.header("Riepilogo")
    col5, col6, = st.columns(2)
    tempo_lavorazioni_aggiuntive=col5.number_input(
        "minuti lavorazioni aggiuntive da conteggiare separatamente (es. maschiatura/filettatura TR, ripulitura alle spazzole etc..) ", 
         value = 0, step = 1)
    n_piazzatura=col5.number_input("n° macchine (piazzature tornio/trapani/fresa ecc..) utilizzate = ", value = 0, step = 1)
    n_piazzaturaMann=col5.number_input("n° piazzature mannaioni = ", value = 0, step = 1)
    tempo_piazzatura = n_piazzatura*tempo_piazzaturaU + n_piazzaturaMann*tempo_piazzaturaMann
    tempo_tornitura = totaleTornituraEC+totaleTornituraIC
    tempo_altre_lav = totale_tempo_altrelavEC+totale_tempo_altrelavIC+tempo_preforo
    tempo_totale_senza_piazz = totaleEC+totaleIC+tempo_lavorazioni_aggiuntive
    tempo_totale_con_piazz = totaleEC+totaleIC+tempo_piazzatura+tempo_lavorazioni_aggiuntive

    
    st.text("totale tempo tornitura min " + str(tempo_tornitura))
    st.text("totale tempo altre lavorazioni min " + str(tempo_altre_lav))
    st.text("totale tempo lavorazioni aggiuntive min " + str(tempo_lavorazioni_aggiuntive))
    st.text("totale tempo globale lavorazioni (escluso piazzatura) min " + str(tempo_totale_senza_piazz))
    st.text("totale piazzature min " + str(tempo_piazzatura))
    st.text("totale tempo globale lavorazioni con piazzatura min " + str(tempo_totale_con_piazz))


#creazione df tempi di lavorazione
pezzi_in_lav=list(range(0, pezzi_ottimali))

df=pd.DataFrame({'pz': pezzi_in_lav})
df['pz']=df.pz+1
df['piazzatura_totale'] = tempo_piazzatura 


#definizione funzione decremento tempi in base alla quantità
rapporto_incrList = []

for index, row in df.iterrows():
    pz=row['pz']
    rapporto_incr = 1/(pz*(math.log(pezzi_ottimali)))
    rapporto_incrList.append(rapporto_incr)  #aggiunti valori a lista 

rapporto_incrSerie = pd.Series(rapporto_incrList)

#creazione df appoggio per calcoli
df_appoggio=pd.DataFrame({'pz': pezzi_in_lav})
df_appoggio['rapporto_incr']=rapporto_incrSerie
df_appoggio.loc[0,'rapporto_incr']=0

#calcolo tempi in base alla quantità
#tempi tornitura
tempi_tornituraList=[tempo_tornitura]

for index, row in df_appoggio.iterrows():
    ultimo_valore = tempi_tornituraList[-1]
    moltiplicatore = row['rapporto_incr']
    tempo=(ultimo_valore-ultimo_valore*(moltiplicatore))
    tempi_tornituraList.append(tempo)


tempi_tornituraList.pop(0)
tempi_tornituraSerie = pd.Series(tempi_tornituraList)
df['tempi_tornitura'] = tempi_tornituraSerie  
df['tempi_tornitura'] = df['tempi_tornitura'].round()
df['tempi_tornitura'] = df['tempi_tornitura'].astype(int)


#tempi per altre lavorazioni (fresatura/chiavetta/foratura etc)
tempo_altre_lavList=[tempo_altre_lav]

for index, row in df_appoggio.iterrows():
    ultimo_valore = tempo_altre_lavList[-1]
    moltiplicatore = row['rapporto_incr']
    tempo=(ultimo_valore-ultimo_valore*(moltiplicatore))
    tempo_altre_lavList.append(tempo)


tempo_altre_lavList.pop(0)
tempo_altre_lavSerie = pd.Series(tempo_altre_lavList)
df['tempo_altre_lav'] = tempo_altre_lavSerie     
df['tempo_altre_lav'] = df['tempo_altre_lav'].round()
df['tempo_altre_lav'] = df['tempo_altre_lav'].astype(int)

#tempi per lavorazioni aggiuntive
tempo_lavorazioni_aggiuntiveList=[tempo_lavorazioni_aggiuntive]

for index, row in df_appoggio.iterrows():
    ultimo_valore = tempo_lavorazioni_aggiuntiveList[-1]
    moltiplicatore = row['rapporto_incr']
    tempo=(ultimo_valore-ultimo_valore*(moltiplicatore))
    tempo_lavorazioni_aggiuntiveList.append(tempo)


tempo_lavorazioni_aggiuntiveList.pop(0)
tempo_lavorazioni_aggiuntiveSerie = pd.Series(tempo_lavorazioni_aggiuntiveList)
df['tempo_lav_aggiuntive'] = tempo_lavorazioni_aggiuntiveSerie     
df['tempo_lav_aggiuntive'] = df['tempo_lav_aggiuntive'].round()
df['tempo_lav_aggiuntive'] = df['tempo_lav_aggiuntive'].astype(int)

#inserimento tempo preforo

#totale tempi
df['totale_tempo_lav'] = df['tempi_tornitura']+df['tempo_altre_lav']+df['tempo_lav_aggiuntive']
df['totale_tempo_con_Piazzatura']=df['totale_tempo_lav']+(df['piazzatura_totale']/df['pz'])
df['variazione'] = df['totale_tempo_con_Piazzatura'].pct_change()*100

st.dataframe(df)

if tipo_pezzo == 'Viti':
    dictionaryLavVite = {'codice articolo' : codice_articolo,
                         'pz ottimali' : pezzi_ottimali, 
                         'materiale' : materiale,
                         'diametro partenza A': diam_partenzaA,
                         'n° diametri A': n_diametriA,
                         'altre lav torn lato A': [altre_lavTornA],
                         'calcolo asportazione A': totale_calcolo_asportazioneA,
                         'altre lav A': [altre_lavA],
                         'n° diametri B': n_diametriB,
                         'calcolo asportazione B': totale_calcolo_asportazioneB,
                         'altre lav torn lato B': [altre_lavTornB],
                         'altre lav B': [altre_lavB],
                         'tempo lav aggiuntive': tempo_lavorazioni_aggiuntive,
                         'piazzature varie':n_piazzatura,
                         'piazzature mannaioni': n_piazzaturaMann,
                         'piazzature filettatore':n_piazzaturaFil}
    dfRiepilogoLav = pd.DataFrame(data=dictionaryLavVite, index = ['DATI LAV.'])
    dfRiepilogoLav = dfRiepilogoLav.transpose()
    st.dataframe(dfRiepilogoLav,width=2000,height=600) 

if tipo_pezzo == 'Chiocciole':
    dictionaryLavChiocc = {'codice articolo' : codice_articolo,
                         'pz ottimali' : pezzi_ottimali, 
                         'materiale' : materiale,
                         'diametro partenza est. chiocc': diam_partenzaEC,
                         'n° diametri esterno': n_diametriEC,
                         'altre lav torn lato esterno': [altre_lavTornEC],
                         'calcolo asportazione esterno': totale_calcolo_asportazione_EC,
                         'altre lav esterno': [altre_lavEC],
                         'diametro partenza int. chiocc': diam_partenzaIC,
                         'n° diametri interno': n_diametriIC,
                         'calcolo asportazione interno': totale_calcolo_asportazione_IC,
                         'altre lav torn lato interno': [altre_lavTornIC],
                         'altre lav interno': [altre_lavIC],
                         'tempo preforo': tempo_preforo,
                         'tempo lav aggiuntive': tempo_lavorazioni_aggiuntive,
                         'piazzature varie':n_piazzatura,
                         'piazzature mannaioni': n_piazzaturaMann}
    dfRiepilogoLav = pd.DataFrame(data=dictionaryLavChiocc, index = ['DATI LAV.'])
    dfRiepilogoLav = dfRiepilogoLav.transpose()
    st.dataframe(dfRiepilogoLav, width=2000, height=600) 
