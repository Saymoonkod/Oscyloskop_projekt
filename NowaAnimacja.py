import math
import numpy as np
import sounddevice as sd

#Podstawowe dane
FS = 44100
BUFFER_SIZE = 1024

# Generowanie sześcianu
# Punkty sześcianu w przestrzeni 3D (x, y, z)
cube_vertices = np.array([
    [-0.5, -0.5, -0.5],
    [0.5, -0.5, -0.5],
    [0.5, 0.5, -0.5],
    [-0.5, 0.5, -0.5],
    [-0.5, -0.5, 0.5],
    [0.5, -0.5, 0.5],
    [0.5, 0.5, 0.5],
    [-0.5, 0.5, 0.5],
])

# Krawędzie łączące wierzchołki sześcianu
edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),  # tył
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),  # przód
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),  # łączenia
]


def generate_frame(angle):
  # Macierze obrotu wokół osi X i Y
  rad_x = angle
  rad_y = angle * 1.3

  cos_x, sin_x = math.cos(rad_x), math.sin(rad_x)
  cos_y, sin_y = math.cos(rad_y), math.sin(rad_y)

  frame_points = []

  for edge in edges:
    p1 = cube_vertices[edge[0]]
    p2 = cube_vertices[edge[1]]

    for p in [p1, p2]:
      # Obrót Y
      x1 = p[0] * cos_y - p[2] * sin_y
      y1 = p[1]
      z1 = p[0] * sin_y + p[2] * cos_y

      # Obrót X 
      x2 = x1
      y2 = y1 * cos_x - z1 * sin_x

      frame_points.append((x2, y2))

    # Dodanie punktu, aby wiązka nie rysowała linii między osobnymi krawędziami
    frame_points.append((0, 0))

  if not frame_points:
    return np.zeros((BUFFER_SIZE, 2), dtype=np.float32)

  # Zmiana rozmiaru do bufora audio
  px = np.array([pt[0] for pt in frame_points])
  py = np.array([pt[1] for pt in frame_points])

  old_indices = np.linspace(0, 1, len(px))
  new_indices = np.linspace(0, 1, BUFFER_SIZE)

  x = np.interp(new_indices, old_indices, px)
  y = np.interp(new_indices, old_indices, py)

  return np.column_stack((x, y)).astype(np.float32)


# Sygnał audio
current_audio = np.zeros((BUFFER_SIZE, 2), dtype=np.float32)


def audio_callback(outdata, frames, time, status):
  global current_audio
  if len(current_audio) == frames:
    outdata[:] = current_audio
  else:
    outdata[: len(current_audio)] = current_audio
    outdata[len(current_audio) :] = 0


stream = sd.OutputStream(
    samplerate=FS, channels=2, callback=audio_callback, blocksize=BUFFER_SIZE
)
stream.start()

# Ten kod poniżej powoduje, że animacja może się wykonywać
import time as t_lib

angle = 0
try:
  print("Odtwarzanie animacji na oscyloskopie... Naciśnij Ctrl+C, aby zakończyć.")
  while True:
    current_audio = generate_frame(angle)
    angle += 0.03  # Szybkość obrotu
    t_lib.sleep(1 / 60)
except KeyboardInterrupt:
  pass
finally:
  stream.stop()
  stream.close()
