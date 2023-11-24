import asyncpg
import asyncio
import random

class BlackjackGame:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.deck = self.generate_deck()
        self.player_hand = []
        self.dealer_hand = []

    def generate_deck(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]
        random.shuffle(deck)
        return deck

    def calculate_hand_value(self, hand):
        value = 0
        num_aces = 0

        for card in hand:
            if card['rank'].isdigit():
                value += int(card['rank'])
            elif card['rank'] in ['J', 'Q', 'K']:
                value += 10
            elif card['rank'] == 'A':
                value += 11
                num_aces += 1

        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1

        return value

    async def deal_initial_cards(self):
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

    async def hit(self, hand):
        hand.append(self.deck.pop())

    async def stand(self):
        while self.calculate_hand_value(self.dealer_hand) < 17:
            await self.hit(self.dealer_hand)

    async def play(self):
        await self.deal_initial_cards()

        # Логика

        # пока значение руки не станет 17 или больше.
        while self.calculate_hand_value(self.player_hand) < 17:
            await self.hit(self.player_hand)

        await self.stand()

        # Определение победителя
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)

        # Обновление бд
        async with self.db_pool.acquire() as connection:
            await connection.execute("INSERT INTO blackjack_games (player_hand, dealer_hand, player_value, dealer_value) VALUES ($1, $2, $3, $4)", str(self.player_hand), str(self.dealer_hand), player_value, dealer_value)

async def main():
    # PostgreSQL
    db_pool = await asyncpg.create_pool(dsn='db')

    game = BlackjackGame(db_pool)
    await game.play()

if __name__ == "__main__":
    asyncio.run(main())
