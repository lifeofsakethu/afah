class AuraMachine:
    def __init__(self):
        self.colors = ["red", "blue", "green", "purple", "gold", "silver", "pink", "orange"]
        self.vibes = ["chill", "energetic", "mysterious", "peaceful", "chaotic", "balanced"]
        self.intensities = ["weak", "medium", "strong", "overwhelming"]
    
    def generate_aura(self):
        """Generate a random aura reading"""
        color = random.choice(self.colors)
        vibe = random.choice(self.vibes)
        intensity = random.choice(self.intensities)
        
        return {
            "color": color,
            "vibe": vibe,
            "intensity": intensity
        }
    
    def display_aura(self):
        """Display a formatted aura reading"""
        aura = self.generate_aura()
        print(f"✨ Your aura: {aura['intensity'].capitalize()} {aura['color']} {aura['vibe']} energy ✨")