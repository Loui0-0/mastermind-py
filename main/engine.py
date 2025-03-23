import pygame as pg
import random
vec2 = pg.math.Vector2

class Key_Handler:
	"""gere les interactions"""
	def __init__(self):
		self.keys = {}
		self.scroll_offset = 0
		self.mouse_dist = 0
		self.absolute_offset = 0

	def update(self,events):

		for ev in events:
			"""boucle d'events"""
			if ev.type == pg.KEYDOWN:
				self.keys[ev.key] = True

			if ev.type == pg.KEYUP:
				self.keys[ev.key] = False

			if ev.type == pg.MOUSEBUTTONDOWN:
				if ev.button == 1:
					self.keys['leftclick'] = True
					self.keys['leftclickpressed'] = True
					self.mouse_dist = pg.mouse.get_pos()[1]
				if ev.button == 2:
					self.keys['middleclick'] = True
				if ev.button == 3:
					self.keys['rightclick'] = True

			if ev.type == pg.MOUSEBUTTONUP:
				if ev.button == 1:
					self.keys['leftclick'] = False
					self.absolute_offset = self.scroll_offset

				if ev.button == 2:
					self.keys['middleclick'] = False
				if ev.button == 3:
					self.keys['rightclick'] = False

			if ev.type == pg.MOUSEWHEEL: #pour le scrolling molettes 
				self.scroll_offset += ev.y*10
				self.absolute_offset += ev.y*10
			mouse_pos = vec2(pg.mouse.get_pos())
			
			if self.keys.get('leftclick') and mouse_pos.x>40 and mouse_pos.x<340: #pour le draging de haut en bas 
				self.scroll_offset = self.absolute_offset + mouse_pos.y - self.mouse_dist 

				


	def get_scroll_offset(self):
		return self.scroll_offset

	def is_pressed(self,key):
		return self.keys.get(key)

class Mastermind:
	"""gere la partie"""
	def __init__(self,solution = None):
		self.board = []#historique des coups joués
		self.results = []#historique des resultats
		self.current_turn = 1
		self.solution = solution if solution else [random.randint(1,4) for _ in range(4)]


	def play_turn(self,guess_code):
		self.board.append(guess_code)
		place = Mastermind.placement(self.solution,guess_code)
		self.results.append(place)
		self.current_turn+=1
		return place #place : (nb de bien placé, nb de mal placé)

	def loose(self):
		"""lorsque l'on pere on veut afficher la solution"""
		self.board.append(self.solution)
		self.results.append((0,0))

	def placement(l1,l2):#pour trouver bien_p et mal_p
		l1,l2 = l1.copy(),l2.copy()
		bien_p = 0
		for i in range(len(l1)):
			if l1[i] == l2[i]:
				bien_p+=1
				l1[i] = l2[i] = -1
		mal_p = 0
		
		for index,i in enumerate(l1):
			if i in l2 and i!= -1:
				l2[l2.index(i)] = -1
				mal_p +=1
		return bien_p,mal_p



class Slot(pg.sprite.Sprite):
	"""recupere la couleur"""
	def __init__(self,game,number):
		super().__init__() #herite de pg.sprite.Sprite 
		#game
		self.game = game #on lui acces au reste 
		self.current_turn = 1
		self.number = number #entre 0 et 4 

		#entity
		self.pos = vec2(76+self.number*70.5,526-(self.current_turn-1)*78.3) #les positions sont 'hard codé' pour coller avec le background 



		#sprite
		self.color = 0
		self.image = self.game.colors_sprites[self.color] #pygame recupere cette var lors de l'apelle de Sprite.draw(canvas)
		self.rect = self.image.get_rect()
		self.rect.center = self.pos #image centré sur la souris

	def update(self, scrolloffset):
		"""chaque frame on update sa pos et sa couleur"""
		self.pos = vec2(76+self.number*70.5,526-(self.current_turn-1)*78.3+scrolloffset)
		self.image = self.game.colors_sprites[self.color]
		self.rect = self.image.get_rect()
		self.rect.center = self.pos
	
	def play_turn(self):
		self.current_turn+=1
		self.color = 0



class Cursor(pg.sprite.Sprite):
	"""gere les interactions du pointeur de la souris"""
	def __init__(self,game):
		super().__init__()
		#game
		self.game = game
		
		#entity
		self.pos = pg.mouse.get_pos()

		#image
		self.color = 0
		self.image = self.game.colors_sprites[self.color]
		self.rect = self.image.get_rect()
		self.rect.center = self.pos

	def update(self):
		"""s'execute chaque frames"""
		self.pos = pg.mouse.get_pos()

		self.image = self.game.colors_sprites[self.color]#recup du sprite en accord avec sa couleur
		self.rect = self.image.get_rect()
		self.rect.center = self.pos

		#si il y a 'collision' entre le sprite de la souris et un element Color_picker on prend sa couleur 
		for color_picker in self.game.color_pickers_g:
			if self.rect.colliderect(color_picker.rect):
				if self.game.key_handler.is_pressed('leftclick'):
					self.color = color_picker.color

		#si au contraire il y a collision avec un slot on lui donne la couleur 
		for slot in self.game.slots_g:
			if self.rect.colliderect(slot.rect):
				if self.game.key_handler.is_pressed('leftclickpressed'):
					if self.color != 0:
						slot.color = self.color
						self.color = 0
					else: 
						slot.color = (slot.color+1)%5



class Color_picker(pg.sprite.Sprite):
	"""donne simplement une couleur au joueur """
	def __init__(self,game,color):
		super().__init__()
		#game
		self.game = game
		self.color = color

		#entity
		self.pos = vec2(386,186+92*(self.color-1))

		#image
		self.image = self.game.colors_sprites[self.color]
		self.rect = self.image.get_rect()
		self.rect.center = self.pos

