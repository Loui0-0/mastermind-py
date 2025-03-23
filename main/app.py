import pygame as pg
import os
import random
from . import engine
vec2 = pg.math.Vector2



class Game:
	"""
	met en relation les different objets et gere la game loop
	"""
	def __init__(self):

		#importation des sprites dans des dicos pour les retrouver facilement
		self.ui_images = {filename[:-4]:pg.image.load('./assets/backgrounds/'+filename) for filename in os.listdir('./assets/backgrounds/')}
		self.ui_images.update({filename[:-4]:pg.image.load('./assets/widgets/'+filename) for filename in os.listdir('./assets/widgets/')})
		self.colors_sprites = {int(filename[:-4]):pg.image.load('./assets/sprites/Colors/'+filename) for filename in os.listdir('./assets/sprites/Colors/')}

		#initialisation des variable pour le fonctionement de pygame
		pg.init()
		self.SCREENWIDTH,self.SCREENHEIGHT = 438,612 #taille ecran
		self.canvas = pg.display.set_mode((self.SCREENWIDTH,self.SCREENHEIGHT)) #surface de dessin
		pg.display.set_caption('Mastermind')
		
		self.key_handler = engine.Key_Handler() #gere l'input utilisateur
		self.mastermind = engine.Mastermind() #permet de suivre le cours du jeu

		self.slots_g = pg.sprite.Group() #les groups permettent de stocker des sous instances de pg.sprite.Sprite pour les manipuler facilement
		for i in range(0,4):
			self.slots_g.add(engine.Slot(self,i)) #slot est l'objet qui receptionne la couleur
		
		self.color_pickers_g = pg.sprite.Group() #objet qui donne la couleur
		for i in range(1,5):
			self.color_pickers_g.add(engine.Color_picker(self,i))


		self.scroll_offset = 0 #decalage en y du jeu
		self.cursor = engine.Cursor(self) #class special pour la souris pour gerer les interactions 
		self.cursor_g = pg.sprite.GroupSingle(self.cursor)

	def play_turn(self):
		"""joue le tour"""
		code = [slot.color for slot in self.slots_g]
		place = self.mastermind.play_turn(code)

		for slot in self.slots_g:
			slot.play_turn()

		return place 

	def draw_past_board(self):
		"""dessine les coups precedents"""
		if self.mastermind.current_turn > 1:
			for i,code in enumerate(self.mastermind.board):
				for j,color in enumerate(code):
					image = self.colors_sprites[color]
					self.canvas.blit(image,vec2(76+j*70.5,526-i*78+self.scroll_offset)-vec2(image.get_rect().size)//2) #on decale le sprite en fonction de sa position

				for k in range(self.mastermind.results[i][0]):				
					self.canvas.blit(self.ui_images['bien'],vec2(48+k*71,500-i*79+self.scroll_offset))

				for n in range(self.mastermind.results[i][1]):
					self.canvas.blit(self.ui_images['mal'],vec2(259-70*n,500-i*79+self.scroll_offset))

	def draw_selector(self):
		"""contour blanc"""
		current_turn = self.mastermind.current_turn
		self.canvas.blit(self.ui_images['selector'],vec2(42,494-(current_turn-1)*79+self.scroll_offset))

	def reset(self):
		"""quand la partie est finie on reinitialise les variables pour la prochaine"""
		self.scroll_offset = 0
		self.mastermind = engine.Mastermind()
		self.slots_g = pg.sprite.Group()
		for i in range(0,4):
			self.slots_g.add(engine.Slot(self,i))
		self.color_pickers_g = pg.sprite.Group()
		for i in range(1,5):
			self.color_pickers_g.add(engine.Color_picker(self,i))
		self.cursor = engine.Cursor(self)
		self.cursor_g = pg.sprite.GroupSingle(self.cursor)


	def mainloop(self):
		"""la game loop permet d'afficher le jeu et de le faire fonctionner"""

		running = True; result = 'QUIT'

		while running:
			self.canvas.fill((35,31,32))#la couleur de fond
			self.canvas.blit(self.ui_images['emptyboard'],(40,-380+self.scroll_offset))#on dessine le plateau en fonction de scroll_offset

			events = pg.event.get()
			for ev in events: #boucle d'evenement pour quitter si besoin
				if ev.type == pg.QUIT:
					result = 'QUIT'
					running = False

			self.scroll_offset = self.key_handler.get_scroll_offset() #calcule de scroll_offset par key_handler
			
			if self.key_handler.is_pressed(pg.K_SPACE) and not(0 in [slot.color for slot in self.slots_g]): #on ne joue le tour que si les slots ont tous une couleur

				place = self.play_turn()

				if place[0] == 4:#si on a 4 couleur bien placé on gagne
					result = 'win'
					running = False

				elif self.mastermind.current_turn == 13:
					self.mastermind.loose()
					result = 'lost'
					running = False

			self.key_handler.update(events) #on envoie a key_handler les events

			#on update les elements du jeu
			self.cursor_g.update()
			self.slots_g.update(self.scroll_offset)
			
			
			#dessin des elements du jeu
			self.draw_past_board()
			self.draw_selector()
			self.slots_g.draw(self.canvas)
			self.color_pickers_g.draw(self.canvas)			
			
			#reste du background
			self.canvas.blit(self.ui_images['MasterMind'],(0,0))

			self.cursor_g.draw(self.canvas)

			self.key_handler.keys['leftclickpressed'] = False
			pg.display.flip()#update de l'ecran pour afficher les modifs

		return result

	def winscreen(self):
		"""ecran de victoir"""
		running = True; result = 'QUIT'
		while running:
			self.canvas.fill((35,31,32))
			self.canvas.blit(self.ui_images['emptyboard'],(40,-380+self.scroll_offset))
			events = pg.event.get()
			for ev in events:
				if ev.type == pg.QUIT:
					result = 'QUIT'
					running = False

			self.key_handler.update(events)
			self.scroll_offset = self.key_handler.get_scroll_offset()
			if self.key_handler.is_pressed(pg.K_r):
				result='restart'
				running = False
			elif self.key_handler.is_pressed(pg.K_ESCAPE):
				result = 'QUIT'
				running = False


			self.draw_past_board()
			self.canvas.blit(self.ui_images['winscreen'],(0,0))
			pg.display.flip()

		return result

	def lostscreen(self):
		"""ecran de defaite"""

		running = True; result = 'QUIT'
		while running:
			self.canvas.fill((35,31,32))
			self.canvas.blit(self.ui_images['emptyboardsolution'],(40,-460+self.scroll_offset))#ce board contient un ligne en plus pour affiche la soluce
			events = pg.event.get()
			for ev in events:
				if ev.type == pg.QUIT:
					result = 'QUIT'
					running = False

			self.key_handler.update(events)
			self.scroll_offset = self.key_handler.get_scroll_offset()
			if self.key_handler.is_pressed(pg.K_r):
				result='restart'
				running = False
			elif self.key_handler.is_pressed(pg.K_ESCAPE):
				result = 'QUIT'
				running = False


			self.draw_past_board()
			self.canvas.blit(self.ui_images['lostscreen'],(0,0))
			
			pg.display.flip()

		return result
	
	




def run():
	"""fait tourner le jeu"""
	game = Game()
	result = None 
	while result != 'QUIT':
		result = game.mainloop()
		if result == 'win':
			result = game.winscreen()
		elif result == 'lost':
			result = game.lostscreen()
		game.reset()
	pg.quit()