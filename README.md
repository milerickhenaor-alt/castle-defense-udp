"# castle-defense-udp" 
# 🏰 Castle Defense - Socket Edition 🏹

Juego de defensa de torres multijugador en tiempo real desarrollado en **Python** utilizando **Pygame** y comunicación **UDP (Sockets)**. Dos equipos compiten por proteger su fortaleza mientras destruyen la del oponente.

---

## 🧩 Entidades Principales

| Entidad | Descripción | Funciones |
| :--- | :--- | :--- |
| **👤 Jugadores** | Defensores del reino | Movimiento y disparo de proyectiles. |
| **🏰 Castillos** | La base del equipo | Poseen HP (Vida). Si llega a 0, el equipo pierde. |
| **👹 Trolls** | Enemigos automáticos | Avanzan hacia el castillo enemigo para destruirlo. |
| **🏹 Proyectiles** | Flechas de defensa | Creadas por jugadores para eliminar Trolls. |

---

## 🧠 Reglas del Juego

1. **Generación Automática**: Los Trolls aparecen en intervalos regulares desde cada castillo.
2. **Avance Imparable**: Los enemigos caminan en línea recta hacia el castillo rival.
3. **Defensa Activa**: Los jugadores deben disparar a los Trolls para evitar que toquen su castillo.
4. **Colisiones**: 
   - **Flecha vs Troll**: El Troll pierde vida y la flecha desaparece.
   - **Troll vs Castillo**: El castillo recibe daño y el Troll desaparece.
5. **Victoria**: Gana el equipo que destruya el castillo enemigo o tenga mayor puntaje al agotarse el tiempo.

---

## ⚙️ Ciclo de Vida (Game Loop)

El motor del juego corre a **60 FPS**, sincronizando en cada frame:
1. **Input**: Captura de teclas (W, S, Espacio / Flechas, Enter).
2. **Física**: Actualización de posiciones de proyectiles y Trolls.
3. **Lógica de Servidor**: Generación de enemigos y detección de colisiones.
4. **Networking**: Sincronización de posiciones y eventos vía UDP.
5. **Render**: Dibujo de entidades y UI (Puntajes, Tiempo, Vida).

---

## 📡 Sincronización Multijugador

Para garantizar que todos los jugadores vean lo mismo, el sistema sincroniza:
- ✅ Posición exacta de todos los jugadores.
- ✅ Creación y trayectoria de proyectiles.
- ✅ Spawn y vida de los Trolls.
- ✅ Estado de salud de los castillos y fin de partida.

## 🎮 Controles del Juego

### Jugador 1 (Equipo A - Izquierda)
| Acción | Tecla |
| :--- | :--- |
| **Mover Arriba** | `W` |
| **Mover Abajo** | `S` |
| **Disparar** | `F` |

### Jugador 2 (Equipo B - Derecha)
| Acción | Tecla |
| :--- | :--- |
| **Mover Arriba** | `↑` (Flecha Arriba) |
| **Mover Abajo** | `↓` (Flecha Abajo) |
| **Disparar** | `ESPACIO` |

---

## 🚀 Cómo Ejecutar

### Requisitos Previos
- Python 3.8+
- Pip (gestor de paquetes)
- Dos máquinas en red (o localhost para pruebas)

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```
O instala manualmente:
```bash
pip install pygame
```

### Paso 1: Iniciar el Servidor
En una terminal (la máquina serveridora):
```bash
python run_server.py
```
Deberías ver:
```
🚀 SERVIDOR INICIADO EN PUERTO 5000
Esperando conexiones...
```

### Paso 2: Configurar Clientes
Edita `assets/config.properties` en cada máquina cliente:
```properties
server.ip=192.168.1.XXX     # IP de la máquina servidor
server.port=5000             # Puerto del servidor
```

### Paso 3: Iniciar los Clientes
En cada máquina cliente (abre 2 instancias):
```bash
python main.py
```
Espera a que ambos clientes se conecten, luego:
1. Ingresa nombres para tus 2 jugadores
2. Selecciona castillo y tipo de enemigo
3. Presiona "Ready" para que ambos equipos inicien el juego

---

## 📦 Tecnología Utilizada

| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **Python** | 3.8+ | Lenguaje de programación |
| **Pygame** | 2.0+ | Motor de gráficos y eventos |
| **Socket (stdlib)** | - | Comunicación UDP nativa de Python |
| **JSON (stdlib)** | - | Serialización de mensajes |
| **Time (stdlib)** | - | Gestión de tiempos y spawn |
| **UUID (stdlib)** | - | IDs únicos para entidades |
| **Dataclasses (stdlib)** | - | Definición de entidades |
| **Enum (stdlib)** | - | Tipos de mensajes |

### Instalación Mínima
```bash
pip install pygame==2.0.0
```

---

## �🛠️ Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/milerickhenaor-alt/castle-defense-udp)