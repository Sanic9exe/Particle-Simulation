import pygame
import math
import random
import colorsys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60
GRAVITY = 0.2
DAMPING = 0.99
PARTICLE_LIFE = 180  # frames (default for most particles)
MAX_PARTICLES = 5000 # Increased max particles for more dynamic effects

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Particle:
    def __init__(self, x, y, vx, vy, color, size=3, special_type=None, target_pos=None, initial_life=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        
        # Set life based on initial_life or default PARTICLE_LIFE
        self.life = initial_life if initial_life is not None else PARTICLE_LIFE
        self.max_life = initial_life if initial_life is not None else PARTICLE_LIFE

        self.trail = [(x, y)]
        self.max_trail = 15
        self.special_type = special_type
        self.age = 0
        self.rotation = 0
        self.spin_speed = random.uniform(-0.2, 0.2)
        self.target_pos = target_pos # For attractor/blackhole/vortex/gravity_field/explosion_implosion modes
        self.initial_size = size # Store initial size for modes that change size

        # Initialize current_color and current_size to prevent AttributeError
        # They will be updated in the first call to self.update()
        self.current_color = self.color
        self.current_size = self.size

        # Specific attributes for certain modes
        if self.special_type == "lightning":
            self.branch_timer = random.randint(10, 30) # Time until it might branch
            self.branched = False
        elif self.special_type == "firefly":
            self.pulse_offset = random.uniform(0, math.pi * 2) # For pulsating glow
            self.pulse_speed = random.uniform(0.05, 0.15)
        elif self.special_type == "solar":
            self.initial_speed = math.hypot(vx, vy) # Store initial speed for corona effect
        elif self.special_type == "geyser":
            self.initial_y = y # Store initial Y for geyser behavior
        elif self.special_type == "explosion_implosion":
            self.origin_pos = (x, y) # Store origin for implosion effect
        elif self.special_type == "pixel_painter":
            self.target_x = x # For pixel painter, particles try to stay at their spawn point
            self.target_y = y
            self.vx = 0 # Start static
            self.vy = 0
            self.life = PARTICLE_LIFE * 5 # Live much longer for persistent pixels
            self.max_life = self.life
            self.size = random.randint(3, 6) # Fixed size for pixels
        elif self.special_type == "light_tracer":
            self.max_trail = 100 # Very long trail
            self.life = PARTICLE_LIFE * 2 # Longer life
            self.max_life = self.life
            self.size = 2 # Small particle
        elif self.special_type == "sound_visualizer":
            self.base_size = size
            self.pulse_offset = random.uniform(0, math.pi * 2)
        elif self.special_type == "constellation":
            self.life = PARTICLE_LIFE * 10 # Very long life for constellations
            self.max_life = self.life


    def update(self, mouse_pos=None, mouse_buttons=None, all_particles=None, simulated_beat=0): # Added all_particles and simulated_beat
        self.age += 1
        self.rotation += self.spin_speed
        
        # Apply physics (reduced for some special types)
        # Default gravity application
        if self.special_type not in ["bubble", "snow", "smoke", "rain", "firefly", "nebula", "solar", "blackhole", "fluid", "aurora", "swarm", "flowing_stream", "wave_ripple", "path_follower", "explosion_implosion", "pixel_painter", "spring_attraction", "chain_explosion", "light_tracer", "sound_visualizer", "constellation"]:
            self.vy += GRAVITY
        
        # Special behaviors based on particle type
        if self.special_type == "electric":
            # Electric particles zigzag
            self.vx += random.uniform(-1, 1)
            self.vy += random.uniform(-0.5, 0.5)
        elif self.special_type == "magnetic":
            # Magnetic particles curve
            self.vx += math.sin(self.age * 0.1) * 0.5
            self.vy += math.cos(self.age * 0.1) * 0.3
        elif self.special_type == "bubble":
            # Bubbles float upward
            self.vy -= 0.3
            self.vx += random.uniform(-0.2, 0.2)
        elif self.special_type == "snow":
            # Snow drifts slowly
            self.vx += math.sin(self.age * 0.05) * 0.2
            self.vy = abs(self.vy) * 0.3  # Always fall down slowly
        elif self.special_type == "spiral":
            # Spiral particles rotate around their path
            angle = self.age * 0.2
            self.vx += math.cos(angle) * 0.3
            self.vy += math.sin(angle) * 0.3
        elif self.special_type == "rain":
            # Rain falls mostly straight, slight wind
            self.vy += GRAVITY * 0.5 # Less affected by gravity
            self.vx += random.uniform(-0.1, 0.1) # Slight horizontal drift
            self.vx *= 0.98 # Less damping
            self.vy *= 0.98 # Less damping
        elif self.special_type == "smoke":
            # Smoke rises and expands
            self.vy -= 0.15 # Rise upward
            self.vx += random.uniform(-0.1, 0.1) # Gentle horizontal drift
            self.size += 0.05 # Expand over time
            self.vx *= 0.95 # Less damping for a floaty feel
            self.vy *= 0.95 # Less damping
        elif self.special_type == "confetti":
            # Confetti flutters down with rotation
            self.vy += GRAVITY * 0.8 # Affected by gravity
            self.vx += math.sin(self.age * 0.1) * 0.5 # Flutter horizontally
            self.spin_speed = random.uniform(-0.5, 0.5) # Faster spin
        elif self.special_type == "attractor" and mouse_pos:
            # Attractor mode: particles drawn to mouse_pos
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 0.1: # Use a small epsilon to prevent division by zero or near-zero
                force_strength = 0.5 / (dist ** 0.5) # Inverse square root for softer attraction
                self.vx += dx / dist * force_strength
                self.vy += dy / dist * force_strength
                # Add a slight tangential force for swirling effect
                self.vx -= dy / dist * 0.05
                self.vy += dx / dist * 0.05
            else: # If very close to the mouse, slow down
                self.vx *= 0.8
                self.vy *= 0.8
        elif self.special_type == "blackhole" and mouse_pos:
            # Blackhole: particles spiral into mouse_pos
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 5: # Avoid extreme forces at center
                # Stronger attraction
                force_strength = 1000 / (dist ** 2) # Inverse square law for stronger pull
                self.vx += dx / dist * force_strength
                self.vy += dy / dist * force_strength
                # Tangential force for spiraling
                self.vx -= dy / dist * (force_strength * 0.5)
                self.vy += dx / dist * (force_strength * 0.5)
            else: # If very close, slow down and eventually disappear
                self.vx *= 0.5
                self.vy *= 0.5
                self.life -= 5 # Accelerate fading
            self.vx *= 0.9 # Less damping to maintain speed
            self.vy *= 0.9 # Less damping
        elif self.special_type == "fluid":
            # Fluid: very low gravity, high damping, gentle movement
            self.vy += GRAVITY * 0.1 # Very slight gravity
            self.vx *= 0.95 # High damping
            self.vy *= 0.95 # High damping
            self.spin_speed = 0 # No rotation
        elif self.special_type == "crystal":
            # Crystal: falls with gravity, rotates
            self.vy += GRAVITY * 0.5 # Slower fall
            self.spin_speed = random.uniform(-0.1, 0.1) # Consistent spin
        elif self.special_type == "lightning":
            # Lightning: erratic movement, short life, potential to branch
            self.vx += random.uniform(-5, 5)
            self.vy += random.uniform(-5, 5)
            self.life -= 1.65 # How visible it is
            self.branch_timer -= 1
            if self.branch_timer <= 0 and not self.branched:
                self.branched = True
                # Return new particles to be created by the system, with slightly longer life
                return [
                    Particle(self.x, self.y, random.uniform(-5, 5), random.uniform(-5, 5), self.color, self.size, "lightning", initial_life=random.randint(20, 40)),
                    Particle(self.x, self.y, random.uniform(-5, 5), random.uniform(-5, 5), self.color, self.size, "lightning", initial_life=random.randint(20, 40))
                ]
        elif self.special_type == "lava":
            # Lava: slow, heavy, emits smoke
            self.vy += GRAVITY * 0.5 # Slow fall
            self.vx *= 0.98
            self.vy *= 0.98
            if self.age % 10 == 0: # Emit smoke periodically
                return [Particle(self.x, self.y, random.uniform(-0.5, 0.5), random.uniform(-1, -0.2), (100, 100, 100), random.randint(3, 6), "smoke")]
        elif self.special_type == "firefly":
            # Firefly: gentle random walk, no gravity, pulsating brightness
            self.vx += random.uniform(-0.1, 0.1)
            self.vy += random.uniform(-0.1, 0.1)
            self.vx *= 0.99
            self.vy *= 0.99
            # Keep within bounds gently
            if self.x < 0 or self.x > WIDTH: self.vx *= -1
            if self.y < 0 or self.y > HEIGHT: self.vy *= -1
        elif self.special_type == "nebula":
            # Nebula: very slow, expands, fades, no gravity
            self.vx *= 0.99
            self.vy *= 0.99
            self.size += 0.1 # Gradually expand
            self.life -= 0.5 # Slower fade
        elif self.special_type == "solar":
            # Solar: strong outward initial velocity, fades with distance/time
            # No additional forces, just initial burst and natural damping
            pass # Forces handled on creation, just damp and fade
        elif self.special_type == "vortex" and mouse_pos:
            # Vortex: particles spiral into mouse_pos, but less aggressively than blackhole
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 1:
                force_strength = 50 / (dist ** 1.5) # Inverse square root for softer attraction
                self.vx += dx / dist * force_strength
                self.vy += dy / dist * force_strength
                # Tangential force for spiraling
                self.vx -= dy / dist * (force_strength * 0.2)
                self.vy += dx / dist * (force_strength * 0.2)
            else: # If very close, slow down
                self.vx *= 0.8
                self.vy *= 0.8
            self.vx *= 0.95 # Some damping
            self.vy *= 0.95 # Some damping
        elif self.special_type == "aurora":
            # Aurora: drifts slowly upward/sideways, very transparent
            self.vy -= 0.05 # Gentle upward drift
            self.vx += math.sin(self.age * 0.02) * 0.1 # Gentle horizontal sway
            self.vx *= 0.99
            self.vy *= 0.99
            self.size += 0.02 # Slowly expand
            self.life -= 0.2 # Very slow fade
        elif self.special_type == "geyser":
            # Geyser: strong initial upward force, then gravity takes over
            # Only apply initial upward force once or based on age
            if self.age < 10: # Initial burst
                self.vy -= 0.5 # Continuous upward push for a short duration
            self.vy += GRAVITY * 0.8 # Gravity pulls it down
            if self.y > self.initial_y + 10: # If it falls below initial point, consider it "splashed"
                self.life = 0 # Mark for removal
                # Could add a splash effect here by returning new small particles
        elif self.special_type == "swarm" and mouse_pos:
            # Swarm: particles try to move towards mouse_pos and stay somewhat together
            # Simple cohesion and attraction to mouse
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 50: # Attract towards mouse if far
                self.vx += dx / dist * 0.1
                self.vy += dy / dist * 0.1
            elif dist < 20: # Repel from mouse if too close
                self.vx -= dx / dist * 0.05
                self.vy -= dy / dist * 0.05
            
            # Add some random movement to make it look organic
            self.vx += random.uniform(-0.1, 0.1)
            self.vy += random.uniform(-0.1, 0.1)

            self.vx *= 0.98 # Damping
            self.vy *= 0.98 # Damping
        elif self.special_type == "gravity_field" and mouse_pos and mouse_buttons:
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.hypot(dx, dy)
            
            if dist > 0.1:
                force_direction = 5 # Attraction by default
                if mouse_buttons[2]: # Right-click for repulsion (button 2 is right mouse button)
                    force_direction = -7
                
                # Inverse square law for stronger force closer to the mouse
                force_strength = 100 / (dist ** 1.5) 
                
                self.vx += dx / dist * force_strength * force_direction
                self.vy += dy / dist * force_strength * force_direction
                
                # Add a slight tangential force for orbiting effect if attracting
                if force_direction == 1:
                    self.vx -= dy / dist * (force_strength * 0.1)
                    self.vy += dx / dist * (force_strength * 0.1)
            else: # If very close to the mouse, slow down
                self.vx *= 0.8
                self.vy *= 0.8
            self.vx *= 0.97 # Some damping
            self.vy *= 0.97 # Some damping
        elif self.special_type == "flowing_stream":
            # Very low gravity, very low damping to maintain flow
            self.vy += GRAVITY * 0.05
            self.vx *= 0.995
            self.vy *= 0.995
            self.size += 0.01 # Slowly expand to give a dissipating effect
            self.life -= 0.5 # Slightly faster fade
        elif self.special_type == "bouncing_collision":
            # Apply normal gravity
            self.vy += GRAVITY
            # Bounce off walls
            if self.x < 0:
                self.x = 0
                self.vx *= -0.8 # Bounce with energy loss
            elif self.x > WIDTH:
                self.x = WIDTH
                self.vx *= -0.8
            if self.y < 0:
                self.y = 0
                self.vy *= -0.8
            elif self.y > HEIGHT:
                self.y = HEIGHT
                self.vy *= -0.8
            self.vx *= DAMPING # Apply general damping
            self.vy *= DAMPING
        elif self.special_type == "explosion_implosion":
            if self.target_pos: # This particle is part of an implosion
                dx = self.target_pos[0] - self.x
                dy = self.target_pos[1] - self.y
                dist = math.hypot(dx, dy)
                if dist > 1:
                    force_strength = 200 / (dist ** 2) # Strong attraction to origin
                    self.vx += dx / dist * force_strength
                    self.vy += dy / dist * force_strength
                else:
                    self.life -= 10 # Accelerate fading if very close to center
            # Apply damping for both explosion and implosion
            self.vx *= 0.95
            self.vy *= 0.95
            self.size -= 0.05 # Shrink over time
        elif self.special_type == "wave_ripple":
            # Particles expand outwards and fade
            self.size += 0.1 # Grow in size
            self.life -= 1 # Fade
            self.vx *= 0.99 # Slight damping
            self.vy *= 0.99 # Slight damping
        elif self.special_type == "path_follower" and mouse_pos:
            # Particles try to follow the mouse's current position
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 10: # Only apply force if not too close
                self.vx += dx / dist * 0.5
                self.vy += dy / dist * 0.5
            
            self.vx *= 0.9 # Damping
            self.vy *= 0.9 # Damping
        elif self.special_type == "spring_attraction" and mouse_pos:
            # Spring-like attraction to mouse
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.hypot(dx, dy)
            spring_constant = 0.05 # How strong the spring is
            if dist > 1:
                self.vx += dx * spring_constant
                self.vy += dy * spring_constant
            
            # Slight repulsion from other particles (simple approximation)
            if all_particles:
                for other_p in all_particles:
                    if other_p is not self and other_p.special_type == "spring_attraction":
                        odx = self.x - other_p.x
                        ody = self.y - other_p.y
                        odist = math.hypot(odx, ody)
                        if 0 < odist < 50: # Repel if too close
                            repel_force = 1 / (odist ** 0.5) # Inverse square root for softer repulsion
                            self.vx += odx / odist * repel_force * 0.1
                            self.vy += ody / odist * repel_force * 0.1
            
            self.vx *= 0.95 # Damping
            self.vy *= 0.95 # Damping
        elif self.special_type == "pixel_painter":
            # Particles try to stay at their target_x, target_y
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            
            # Strong damping to make them settle quickly
            self.vx *= 0.8
            self.vy *= 0.8
            
            # Gentle force to move towards target
            self.vx += dx * 0.05
            self.vy += dy * 0.05
            
            # If very close to target, stop movement
            if math.hypot(dx, dy) < 1:
                self.x = self.target_x
                self.y = self.target_y
                self.vx = 0
                self.vy = 0
        elif self.special_type == "chain_explosion":
            # These particles just move outwards and fade quickly
            self.life -= 5 # Very short life
            self.vx *= 0.98
            self.vy *= 0.98
        elif self.special_type == "light_tracer":
            # Very low damping, almost no gravity
            self.vy += GRAVITY * 0.01 # Minimal gravity
            self.vx *= 0.999 # Very low damping
            self.vy *= 0.999 # Very low damping
        elif self.special_type == "sound_visualizer":
            # Particles pulse in size and brightness based on simulated_beat
            pulse_factor = (math.sin(self.age * 0.1 + self.pulse_offset) + 1) / 2 # 0 to 1
            # Incorporate simulated_beat into the pulse
            self.current_size = max(1, int(self.base_size * (1 + pulse_factor * 0.5 + simulated_beat * 0.8)))
            # No gravity, just drift slightly
            self.vx += random.uniform(-0.05, 0.05)
            self.vy += random.uniform(-0.05, 0.05)
            self.vx *= 0.99
            self.vy *= 0.99
        elif self.special_type == "constellation":
            # Particles drift very slowly, no gravity
            self.vx *= 0.995
            self.vy *= 0.995
            self.vx += random.uniform(-0.02, 0.02)
            self.vy += random.uniform(-0.02, 0.02)


        # Apply general damping (if not overridden by specific type)
        if self.special_type not in ["blackhole", "lightning", "fluid", "rain", "smoke", "firefly", "nebula", "vortex", "aurora", "swarm", "gravity_field", "flowing_stream", "bouncing_collision", "explosion_implosion", "wave_ripple", "path_follower", "spring_attraction", "pixel_painter", "chain_explosion", "light_tracer", "sound_visualizer", "constellation"]:
            self.vx *= DAMPING
            self.vy *= DAMPING
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off walls (except for specific types that pass through or dissipate)
        if self.special_type not in ["rain", "smoke", "nebula", "firefly", "blackhole", "aurora", "geyser", "flowing_stream", "explosion_implosion", "wave_ripple", "path_follower", "chain_explosion", "light_tracer", "sound_visualizer", "constellation"]: # Added new modes
            if self.x < 0:
                self.x = 0
                self.vx *= -0.8
            elif self.x > WIDTH:
                self.x = WIDTH
                self.vx *= -0.8
            if self.y < 0:
                self.y = 0
                self.vy *= -0.8
            elif self.y > HEIGHT:
                self.y = HEIGHT
                self.vy *= -0.8
        elif self.special_type in ["rain", "smoke", "geyser", "flowing_stream", "explosion_implosion", "wave_ripple", "path_follower", "chain_explosion", "light_tracer", "sound_visualizer", "constellation"]: # For these, let them pass through bottom, or reset
            if self.y > HEIGHT + 50 or self.y < -50 or self.x > WIDTH + 50 or self.x < -50: # Disappear far off screen
                self.life = 0 # Mark for removal
        elif self.special_type == "blackhole": # Blackhole particles disappear at center
            if mouse_pos and math.hypot(mouse_pos[0] - self.x, mouse_pos[1] - self.y) < 5:
                self.life = 0
        elif self.special_type == "aurora": # Aurora particles wrap around or dissipate
            if self.y < -50 or self.y > HEIGHT + 50: self.life = 0
            if self.x < -50 or self.x > WIDTH + 50: self.life = 0
            
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
        # Decrease life
        self.life -= 1
        
        # Fade out
        alpha = self.life / self.max_life
        r, g, b = self.color
        
        # Handle pulsating for fireflies
        if self.special_type == "firefly":
            pulse_factor = (math.sin(self.age * self.pulse_speed + self.pulse_offset) + 1) / 2 # 0 to 1
            current_alpha = alpha * (0.5 + pulse_factor * 0.5) # Base transparency + pulse
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.initial_size * (0.8 + pulse_factor * 0.2))) # Size also pulses
        elif self.special_type == "nebula":
            current_alpha = alpha * 0.2 # Very transparent
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size changes in update, not here
        elif self.special_type == "solar":
            # Fade based on distance from origin or time
            # Ensure mouse_pos is available for solar mode
            if mouse_pos:
                distance_ratio = math.hypot(self.x - mouse_pos[0], self.y - mouse_pos[1]) / (self.max_life * self.initial_speed) # Rough distance ratio
                current_alpha = max(0, alpha - distance_ratio * 0.5) # Fade faster with distance
            else: # Fallback if mouse_pos somehow not passed (shouldn't happen in solar mode)
                current_alpha = alpha
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size * current_alpha)) # Size also fades
        elif self.special_type == "aurora":
            current_alpha = alpha * 0.3 # More transparent for aurora effect
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size changes in update, not here
        elif self.special_type == "flowing_stream":
            current_alpha = alpha * 0.8 # Slightly transparent
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size changes in update, not here
        elif self.special_type == "explosion_implosion":
            current_alpha = alpha # Full alpha, fades with life
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size changes in update, not here
        elif self.special_type == "wave_ripple":
            current_alpha = alpha * 0.4 # Very transparent
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size changes in update, not here
        elif self.special_type == "path_follower":
            current_alpha = alpha # Standard fade
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size changes in update, not here
        elif self.special_type == "spring_attraction":
            current_alpha = alpha # Standard fade
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size changes in update, not here
        elif self.special_type == "pixel_painter":
            current_alpha = alpha # Standard fade, but longer life
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size is mostly fixed
        elif self.special_type == "chain_explosion":
            current_alpha = alpha # Fast fade
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size * alpha)) # Shrink as it fades
        elif self.special_type == "light_tracer":
            current_alpha = alpha * 0.7 # More transparent for long trails
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size is fixed
        elif self.special_type == "sound_visualizer":
            # Color also pulses with beat
            pulse_color_factor = (math.sin(self.age * 0.1 + self.pulse_offset) + 1) / 2
            current_alpha = alpha * (0.5 + pulse_color_factor * 0.5)
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            # Size is handled in update method
        elif self.special_type == "constellation":
            current_alpha = alpha * 0.8 # Slightly transparent
            self.current_color = (int(r * current_alpha), int(g * current_alpha), int(b * current_alpha))
            self.current_size = max(1, int(self.size)) # Size changes in update, not here
        else:
            self.current_color = (int(r * alpha), int(g * alpha), int(b * alpha))
            self.current_size = max(1, int(self.size * alpha))
        
        # Return any new particles generated (e.g., for branching lightning, lava smoke, chain reaction)
        if self.special_type == "lightning" and self.branched:
            self.branched = False # Reset to prevent continuous branching from one particle
            return [
                Particle(self.x, self.y, random.uniform(-5, 5), random.uniform(-5, 5), self.color, self.size, "lightning", initial_life=random.randint(20, 40)),
                Particle(self.x, self.y, random.uniform(-5, 5), random.uniform(-5, 5), self.color, self.size, "lightning", initial_life=random.randint(20, 40))
            ]
        elif self.special_type == "lava" and self.age % 10 == 0:
            return [Particle(self.x, self.y, random.uniform(-0.5, 0.5), random.uniform(-1, -0.2), (100, 100, 100), random.randint(3, 6), "smoke")]
        elif self.special_type == "chain_starter":
            # This particle immediately triggers an explosion and then dies
            self.life = 0 # Mark for removal
            new_burst_particles = []
            for _ in range(random.randint(10, 20)): # Create a burst of particles
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(5, 10)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                new_burst_particles.append(Particle(self.x, self.y, vx, vy, self.color, random.randint(3, 6), "chain_explosion", initial_life=random.randint(20, 40)))
            return new_burst_particles
        return [] # Default: no new particles

    def draw(self, screen):
        # Draw trail
        for i, pos in enumerate(self.trail[:-1]):
            alpha = (i / len(self.trail)) * (self.life / self.max_life)
            if alpha > 0:
                trail_color = (int(self.color[0] * alpha * 0.5), 
                             int(self.color[1] * alpha * 0.5), 
                             int(self.color[2] * alpha * 0.5))
                trail_size = max(1, int(self.current_size * alpha * 0.5)) # Thinner trail
                pygame.draw.circle(screen, trail_color, (int(pos[0]), int(pos[1])), trail_size)
        
        # Draw particle with special effects
        if self.life > 0:
            x, y = int(self.x), int(self.y)
            
            if self.special_type == "electric":
                # Electric particles with lightning effect
                for i in range(3):
                    offset_x = random.randint(-3, 3)
                    offset_y = random.randint(-3, 3)
                    pygame.draw.circle(screen, (255, 255, 100), 
                                     (x + offset_x, y + offset_y), 1)
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                
            elif self.special_type == "bubble":
                # Bubble with highlight
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                pygame.draw.circle(screen, (255, 255, 255), 
                                 (x - self.current_size//3, y - self.current_size//3), 
                                 max(1, self.current_size//3))
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size, 2)
                
            elif self.special_type == "snow":
                # Snowflake shape
                for angle in range(0, 360, 60):
                    end_x = x + math.cos(math.radians(angle + self.rotation)) * self.current_size
                    end_y = y + math.sin(math.radians(angle + self.rotation)) * self.current_size
                    pygame.draw.line(screen, self.current_color, (x, y), (end_x, end_y), 1)
                pygame.draw.circle(screen, self.current_color, (x, y), 2)
                
            elif self.special_type == "spiral":
                # Spiral with rotating arms
                for i in range(4):
                    angle = self.rotation + i * math.pi / 2
                    end_x = x + math.cos(angle) * self.current_size * 2
                    end_y = y + math.sin(angle) * self.current_size * 2
                    pygame.draw.line(screen, self.current_color, (x, y), (end_x, end_y), 2)
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
            
            elif self.special_type == "rain":
                # Draw as a small line for raindrop effect
                line_length = self.current_size * 2
                end_x = x - self.vx * 0.5
                end_y = y - self.vy * 0.5
                pygame.draw.line(screen, self.current_color, (x, y), (end_x, end_y), 1)
                
            elif self.special_type == "smoke":
                # Draw as a soft, larger circle
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                
            elif self.special_type == "confetti":
                # Draw as a rotating rectangle/square
                half_size = self.current_size / 2
                points = [
                    (x + half_size * math.cos(self.rotation) - half_size * math.sin(self.rotation),
                     y + half_size * math.sin(self.rotation) + half_size * math.cos(self.rotation)),
                    (x - half_size * math.cos(self.rotation) - half_size * math.sin(self.rotation),
                     y - half_size * math.sin(self.rotation) + half_size * math.cos(self.rotation)),
                    (x - half_size * math.cos(self.rotation) + half_size * math.sin(self.rotation),
                     y - half_size * math.sin(self.rotation) - half_size * math.cos(self.rotation)),
                    (x + half_size * math.cos(self.rotation) + half_size * math.sin(self.rotation),
                     y + half_size * math.sin(self.rotation) - half_size * math.cos(self.rotation))
                ]
                pygame.draw.polygon(screen, self.current_color, points)
            
            elif self.special_type == "blackhole":
                # Draw as small, dark, intense circles
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                
            elif self.special_type == "fluid":
                # Draw as slightly larger, solid circles
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)

            elif self.special_type == "crystal":
                # Draw as a rotating square
                half_size = self.current_size / 2
                points = [
                    (x + half_size * math.cos(self.rotation) - half_size * math.sin(self.rotation),
                     y + half_size * math.sin(self.rotation) + half_size * math.cos(self.rotation)),
                    (x - half_size * math.cos(self.rotation) - half_size * math.sin(self.rotation),
                     y - half_size * math.sin(self.rotation) + half_size * math.cos(self.rotation)),
                    (x - half_size * math.cos(self.rotation) + half_size * math.sin(self.rotation),
                     y - half_size * math.sin(self.rotation) - half_size * math.cos(self.rotation)),
                    (x + half_size * math.cos(self.rotation) + half_size * math.sin(self.rotation),
                     y + half_size * math.sin(self.rotation) - half_size * math.cos(self.rotation))
                ]
                pygame.draw.polygon(screen, self.current_color, points)
                
            elif self.special_type == "lightning":
                # Draw as a very bright, small circle
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                # Add a bright glow
                pygame.draw.circle(screen, (255, 255, 255), (x, y), self.current_size + 1, 1)

            elif self.special_type == "lava":
                # Draw as a large, glowing circle
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                # Add inner glow
                pygame.draw.circle(screen, (min(255, self.current_color[0] + 50),
                                            min(255, self.current_color[1] + 50),
                                            min(255, self.current_color[2] + 50)),
                                   (x, y), self.current_size - 2, 1)

            elif self.special_type == "firefly":
                # Draw as a small, soft glowing circle
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                # Add a larger, very faint outer glow
                glow_alpha = int((self.current_color[0] + self.current_color[1] + self.current_color[2]) / 3 * 0.1)
                glow_color = (self.current_color[0], self.current_color[1], self.current_color[2], glow_alpha)
                # Pygame draw.circle doesn't support alpha directly, so we'll draw a surface
                s = pygame.Surface((self.current_size * 4, self.current_size * 4), pygame.SRCALPHA)
                pygame.draw.circle(s, glow_color, (self.current_size * 2, self.current_size * 2), self.current_size * 1.5)
                screen.blit(s, (x - self.current_size * 2, y - self.current_size * 2))

            elif self.special_type == "nebula":
                # Draw as a very large, soft, transparent circle
                s = pygame.Surface((self.current_size * 4, self.current_size * 4), pygame.SRCALPHA)
                current_alpha = int(self.current_color[0] / self.color[0] * 255) if self.color[0] > 0 else 0
                nebula_color = (self.color[0], self.color[1], self.color[2], int(current_alpha * 0.1)) # Very low alpha
                pygame.draw.circle(s, nebula_color, (self.current_size * 2, self.current_size * 2), self.current_size * 2)
                screen.blit(s, (x - self.current_size * 2, y - self.current_size * 2))

            elif self.special_type == "solar":
                # Draw as a bright core with a larger, fading corona
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                # Corona effect
                corona_alpha = int(self.current_color[0] / self.color[0] * 255 * 0.3) if self.color[0] > 0 else 0
                corona_color = (self.color[0], self.color[1], self.color[2], corona_alpha)
                s = pygame.Surface((self.current_size * 6, self.current_size * 6), pygame.SRCALPHA)
                pygame.draw.circle(s, corona_color, (self.current_size * 3, self.current_size * 3), self.current_size * 2.5)
                screen.blit(s, (x - self.current_size * 3, y - self.current_size * 3))
            
            elif self.special_type == "vortex":
                # Draw as small, slightly glowing circles
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                glow_color = (min(255, self.current_color[0] + 30),
                              min(255, self.current_color[1] + 30),
                              min(255, self.current_color[2] + 30))
                pygame.draw.circle(screen, glow_color, (x, y), self.current_size + 1, 1)

            elif self.special_type == "aurora":
                # Draw as elongated, very transparent shapes or lines
                # Using a surface for alpha blending
                s = pygame.Surface((self.current_size * 4, self.current_size * 4), pygame.SRCALPHA)
                current_alpha = int(self.current_color[0] / self.color[0] * 255) if self.color[0] > 0 else 0
                aurora_color = (self.color[0], self.color[1], self.color[2], int(current_alpha * 0.15)) # Very low alpha
                
                # Draw an elongated ellipse for a ribbon effect
                ellipse_rect = pygame.Rect(0, 0, self.current_size * 3, self.current_size)
                ellipse_rect.center = (self.current_size * 2, self.current_size * 2)
                pygame.draw.ellipse(s, aurora_color, ellipse_rect, 0)
                
                # Rotate the surface to give a flowing look
                rotated_s = pygame.transform.rotate(s, self.rotation)
                rotated_rect = rotated_s.get_rect(center=(x, y))
                screen.blit(rotated_s, rotated_rect)

            elif self.special_type == "geyser":
                # Draw as simple circles, maybe with a slight trail
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                
            elif self.special_type == "swarm":
                # Draw as small triangles pointing in direction of velocity
                if math.hypot(self.vx, self.vy) > 0.1: # Only if moving
                    angle = math.atan2(self.vy, self.vx)
                    # Create a triangle pointing in the direction of movement
                    p1 = (x + self.current_size * math.cos(angle), y + self.current_size * math.sin(angle))
                    p2 = (x + self.current_size * 0.5 * math.cos(angle - 2*math.pi/3), y + self.current_size * 0.5 * math.sin(angle - 2*math.pi/3))
                    p3 = (x + self.current_size * 0.5 * math.cos(angle + 2*math.pi/3), y + self.current_size * 0.5 * math.sin(angle + 2*math.pi/3))
                    pygame.draw.polygon(screen, self.current_color, [p1, p2, p3])
                else:
                    pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
            
            elif self.special_type == "gravity_field":
                # Draw as a glowing circle, color indicating attraction/repulsion
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                glow_color = (min(255, self.current_color[0] + 20),
                              min(255, self.current_color[1] + 20),
                              min(255, self.current_color[2] + 20))
                pygame.draw.circle(screen, glow_color, (x, y), self.current_size + 2, 1)

            elif self.special_type == "flowing_stream":
                # Draw as small, slightly transparent circles
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
            
            elif self.special_type == "bouncing_collision":
                # Draw as solid, distinct circles
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
            
            elif self.special_type == "explosion_implosion":
                # Draw as a solid circle, shrinking/fading
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)

            elif self.special_type == "wave_ripple":
                # Draw as a very transparent, expanding circle
                s = pygame.Surface((self.current_size * 4, self.current_size * 4), pygame.SRCALPHA)
                current_alpha = int(self.current_color[0] / self.color[0] * 255) if self.color[0] > 0 else 0
                ripple_color = (self.color[0], self.color[1], self.color[2], int(current_alpha * 0.1)) # Very low alpha
                pygame.draw.circle(s, ripple_color, (self.current_size * 2, self.current_size * 2), self.current_size * 2)
                screen.blit(s, (x - self.current_size * 2, y - self.current_size * 2))

            elif self.special_type == "path_follower":
                # Draw as small, distinct circles with a trail
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)

            elif self.special_type == "spring_attraction":
                # Draw as a glowing circle
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                glow_color = (min(255, self.current_color[0] + 30),
                              min(255, self.current_color[1] + 30),
                              min(255, self.current_color[2] + 30))
                pygame.draw.circle(screen, glow_color, (x, y), self.current_size + 1, 1)
            
            elif self.special_type == "pixel_painter":
                # Draw as a solid square for a pixel effect
                pygame.draw.rect(screen, self.current_color, (x - self.current_size/2, y - self.current_size/2, self.current_size, self.current_size))

            elif self.special_type == "chain_explosion":
                # Draw as small, bright, fading circles
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)

            elif self.special_type == "light_tracer":
                # Draw as a small, bright point
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                
            elif self.special_type == "sound_visualizer":
                # Draw as a pulsating circle
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                # Add a subtle outer glow that also pulses
                glow_alpha = int((self.current_color[0] + self.current_color[1] + self.current_color[2]) / 3 * 0.05)
                glow_color = (self.color[0], self.color[1], self.color[2], glow_alpha)
                s = pygame.Surface((self.current_size * 4, self.current_size * 4), pygame.SRCALPHA)
                pygame.draw.circle(s, glow_color, (self.current_size * 2, self.current_size * 2), self.current_size * 1.5)
                screen.blit(s, (x - self.current_size * 2, y - self.current_size * 2))

            elif self.special_type == "constellation":
                # Draw as a small, slightly glowing star-like particle
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                glow_color = (min(255, self.current_color[0] + 20),
                              min(255, self.current_color[1] + 20),
                              min(255, self.current_color[2] + 20))
                pygame.draw.circle(screen, glow_color, (x, y), self.current_size + 1, 1)
                
            else:
                # Default particle
                pygame.draw.circle(screen, self.current_color, (x, y), self.current_size)
                # Add glow effect
                glow_color = (min(255, self.current_color[0] + 50),
                             min(255, self.current_color[1] + 50),
                             min(255, self.current_color[2] + 50))
                pygame.draw.circle(screen, glow_color, (x, y), self.current_size + 2, 1)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.emitters = []
        self.mode = "fountain"  # All modes: fountain, fireworks, paint, electric, bubbles, snow, spiral, galaxy, tornado, rain, smoke, confetti, attractor, blackhole, fluid, crystal, lightning, lava, firefly, nebula, solar, vortex, aurora, geyser, swarm, gravity_field, flowing_stream, bouncing_collision, explosion_implosion, wave_ripple, path_follower, spring_attraction, pixel_painter, chain_reaction, light_tracer, sound_visualizer, constellation
        self.pixel_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
        self.pixel_color_index = 0
        self.simulated_beat_timer = 0
        self.simulated_beat_frequency = 0.05 # How fast the beat pulses (higher = faster)
        self.simulated_beat_strength = 0 # Current strength of the beat (0 to 1)

    def get_next_pixel_color(self):
        color = self.pixel_colors[self.pixel_color_index]
        self.pixel_color_index = (self.pixel_color_index + 1) % len(self.pixel_colors)
        return color
        
    def create_fountain(self, x, y):
        for _ in range(5):
            angle = random.uniform(-math.pi/3, -2*math.pi/3)
            speed = random.uniform(5, 15)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Rainbow colors
            hue = random.random()
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, vx, vy, color, size))
            
    def create_firework(self, x, y):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 20)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Warm explosion colors
            colors = [(255, 100, 100), (255, 200, 100), (255, 255, 100), 
                     (255, 150, 200), (200, 100, 255)]
            color = random.choice(colors)
            
            size = random.randint(3, 6)
            self.particles.append(Particle(x, y, vx, vy, color, size))
            
    def create_paint_splash(self, x, y, mouse_vel):
        for _ in range(8):
            angle = random.uniform(-math.pi/4, math.pi/4)
            speed = random.uniform(3, 12)
            vx = math.cos(angle) * speed + mouse_vel[0] * 0.3
            vy = math.sin(angle) * speed + mouse_vel[1] * 0.3
            
            # Cool paint colors
            colors = [(100, 150, 255), (150, 100, 255), (100, 255, 150), 
                     (255, 100, 150), (255, 255, 100)]
            color = random.choice(colors)
            
            size = random.randint(4, 8)
            self.particles.append(Particle(x, y, vx, vy, color, size))
            
    def create_electric_storm(self, x, y):
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Electric colors
            colors = [(40, 0, 80), (80, 0, 120), (30, 30, 30)]
            color = random.choice(colors)
            
            size = random.randint(2, 4)
            self.particles.append(Particle(x, y, vx, vy, color, size, "electric"))
            
    def create_bubbles(self, x, y):
        for _ in range(4):
            vx = random.uniform(-2, 2)
            vy = random.uniform(-5, -1)
            
            # Bubble colors
            colors = [(100, 200, 255), (150, 220, 255), (200, 240, 255), (255, 255, 255)]
            color = random.choice(colors)
            
            size = random.randint(5, 12)
            self.particles.append(Particle(x, y, vx, vy, color, size, "bubble"))
            
    def create_snow(self, x, y):
        for _ in range(6):
            vx = random.uniform(-1, 1)
            vy = random.uniform(0.5, 3)
            
            # Snow colors
            colors = [(255, 255, 255), (240, 240, 255), (220, 220, 255)]
            color = random.choice(colors)
            
            size = random.randint(3, 6)
            self.particles.append(Particle(x, y, vx, vy, color, size, "snow"))
            
    def create_spiral(self, x, y):
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Spiral colors
            colors = [(255, 100, 255), (255, 150, 100), (100, 255, 255), (255, 255, 100)]
            color = random.choice(colors)
            
            size = random.randint(3, 5)
            self.particles.append(Particle(x, y, vx, vy, color, size, "spiral"))
            
    def create_galaxy(self, x, y):
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, 50)
            start_x = x + math.cos(angle) * distance
            start_y = y + math.sin(angle) * distance
            
            vx = -math.sin(angle) * 3 + random.uniform(-1, 1)
            vy = math.cos(angle) * 3 + random.uniform(-1, 1)
            
            colors = [(150, 100, 255), (100, 150, 255), (255, 200, 100), (255, 100, 200)]
            color = random.choice(colors)
            
            size = random.randint(2, 4)
            self.particles.append(Particle(start_x, start_y, vx, vy, color, size, "magnetic"))
            
    def create_tornado(self, x, y):
        for _ in range(6):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(5, 25)
            start_x = x + math.cos(angle) * radius
            start_y = y + random.uniform(0, 30)
            
            vx = -math.sin(angle) * 4
            vy = random.uniform(-8, -3)
            
            colors = [(200, 200, 200), (150, 150, 150), (180, 180, 180), (220, 220, 220)]
            color = random.choice(colors)
            
            size = random.randint(2, 5)
            self.particles.append(Particle(start_x, start_y, vx, vy, color, size, "spiral"))

    def create_rain(self, x, y):
        for _ in range(3):
            start_x = x + random.uniform(-20, 20)
            start_y = y - random.uniform(50, 100)
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(5, 10)
            
            colors = [(100, 150, 200), (120, 170, 220), (150, 180, 230), (180, 200, 240)]
            color = random.choice(colors)
            
            size = random.randint(1, 3)
            self.particles.append(Particle(start_x, start_y, vx, vy, color, size, "rain"))

    def create_smoke(self, x, y):
        for _ in range(2):
            vx = random.uniform(-1, 1)
            vy = random.uniform(-2, -0.5)
            
            colors = [(100, 100, 100), (150, 150, 150), (200, 200, 200), (230, 230, 230)]
            color = random.choice(colors)
            
            size = random.randint(5, 10)
            self.particles.append(Particle(x, y, vx, vy, color, size, "smoke"))

    def create_confetti(self, x, y):
        for _ in range(5):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, 0)
            
            hue = random.random()
            rgb = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            size = random.randint(4, 7)
            self.particles.append(Particle(x, y, vx, vy, color, size, "confetti"))

    def create_attractor(self, x, y):
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            colors = [(50, 0, 50), (0, 50, 50), (50, 50, 0), (20, 20, 20)]
            color = random.choice(colors)
            
            size = random.randint(2, 4)
            self.particles.append(Particle(x, y, vx, vy, color, size, "attractor", (x, y)))

    def create_blackhole(self, x, y):
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 150)
            start_x = x + math.cos(angle) * distance
            start_y = y + math.sin(angle) * distance
            
            speed = random.uniform(0.5, 2)
            vx = -math.cos(angle) * speed * 0.5 - math.sin(angle) * speed * 0.5
            vy = -math.sin(angle) * speed * 0.5 + math.cos(angle) * speed * 0.5
            
            colors = [(40, 0, 80), (80, 0, 120), (30, 30, 30)]
            color = random.choice(colors)
            
            size = random.randint(2, 5)
            self.particles.append(Particle(start_x, start_y, vx, vy, color, size, "blackhole", (x, y)))

    def create_fluid(self, x, y):
        for _ in range(10):
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            
            colors = [(50, 100, 200), (70, 120, 220), (90, 140, 240)]
            color = random.choice(colors)
            
            size = random.randint(6, 10)
            self.particles.append(Particle(x, y, vx, vy, color, size, "fluid"))

    def create_crystal(self, x, y):
        for _ in range(4):
            vx = random.uniform(-2, 2)
            vy = random.uniform(-3, 0)
            
            colors = [(150, 200, 255), (200, 255, 255), (255, 255, 255), (100, 150, 200)]
            color = random.choice(colors)
            
            size = random.randint(5, 8)
            self.particles.append(Particle(x, y, vx, vy, color, size, "crystal"))

    def create_lightning(self, x, y):
        color = (255, 255, 150)
        size = random.randint(2, 4)
        vx = random.uniform(-5, 5)
        vy = random.uniform(-5, 5)
        self.particles.append(Particle(x, y, vx, vy, color, size, "lightning", initial_life=60)) 

    def create_lava(self, x, y):
        for _ in range(3):
            vx = random.uniform(-1, 1)
            vy = random.uniform(-3, -1)
            
            colors = [(255, 50, 0), (255, 100, 0), (255, 150, 0), (200, 50, 0)]
            color = random.choice(colors)
            
            size = random.randint(8, 15)
            self.particles.append(Particle(x, y, vx, vy, color, size, "lava"))

    def create_firefly(self, x, y):
        for _ in range(2):
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.5, 0.5)
            
            colors = [(150, 255, 150), (200, 255, 200), (255, 255, 150), (100, 200, 255)]
            color = random.choice(colors)
            
            size = random.randint(3, 6)
            self.particles.append(Particle(x, y, vx, vy, color, size, "firefly"))

    def create_nebula(self, x, y):
        for _ in range(1):
            vx = random.uniform(-0.1, 0.1)
            vy = random.uniform(-0.1, 0.1)
            
            colors = [(100, 0, 150), (0, 100, 150), (150, 50, 0), (0, 150, 100), (100, 100, 200)]
            color = random.choice(colors)
            
            size = random.randint(20, 50)
            self.particles.append(Particle(x, y, vx, vy, color, size, "nebula"))

    def create_solar(self, x, y):
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            colors = [(255, 200, 0), (255, 150, 0), (255, 100, 0), (255, 255, 0)]
            color = random.choice(colors)
            
            size = random.randint(4, 8)
            self.particles.append(Particle(x, y, vx, vy, color, size, "solar", (x,y)))

    def create_vortex(self, x, y):
        for _ in range(10):
            offset_angle = random.uniform(0, 2 * math.pi)
            offset_distance = random.uniform(10, 50)
            start_x = x + math.cos(offset_angle) * offset_distance
            start_y = y + math.sin(offset_angle) * offset_distance
            
            vx = -math.sin(offset_angle) * 2 + random.uniform(-1, 1)
            vy = math.cos(offset_angle) * 2 + random.uniform(-1, 1)
            
            colors = [(0, 50, 100), (0, 100, 150), (50, 0, 100), (0, 80, 80)]
            color = random.choice(colors)
            
            size = random.randint(2, 4)
            self.particles.append(Particle(start_x, start_y, vx, vy, color, size, "vortex", (x,y)))

    def create_aurora(self, x, y):
        for _ in range(3):
            start_x = random.uniform(0, WIDTH)
            start_y = HEIGHT + random.uniform(0, 20)
            
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-1, -0.5)
            
            colors = [(50, 200, 50), (100, 255, 100), (0, 150, 200), (50, 50, 200), (150, 0, 200)]
            color = random.choice(colors)
            
            size = random.randint(10, 30)
            self.particles.append(Particle(start_x, start_y, vx, vy, color, size, "aurora", initial_life=300))

    def create_geyser(self, x, y):
        for _ in range(15):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-20, -10)
            
            colors = [(150, 200, 255), (200, 220, 255), (255, 255, 255), (100, 150, 200)]
            color = random.choice(colors)
            
            size = random.randint(3, 6)
            self.particles.append(Particle(x, y, vx, vy, color, size, "geyser", initial_life=90))

    def create_swarm(self, x, y):
        for _ in range(5):
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-10, 10)
            start_x = x + offset_x
            start_y = y + offset_y

            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            
            colors = [(100, 100, 100), (80, 80, 80), (120, 120, 120), (50, 50, 50)]
            color = random.choice(colors)
            
            size = random.randint(2, 4)
            self.particles.append(Particle(start_x, start_y, vx, vy, color, size, "swarm", initial_life=PARTICLE_LIFE))

    def create_gravity_field(self, x, y):
        for _ in range(8):
            start_x = random.uniform(0, WIDTH)
            start_y = random.uniform(0, HEIGHT)
            vx = random.uniform(-3, 3)
            vy = random.uniform(-3, 3)
            
            colors = [(50, 50, 150), (80, 80, 180), (100, 100, 200), (150, 50, 150), (180, 80, 180)]
            color = random.choice(colors)
            
            size = random.randint(3, 6)
            self.particles.append(Particle(start_x, start_y, vx, vy, color, size, "gravity_field"))

    def create_flowing_stream(self, x, y, mouse_vel):
        for _ in range(3):
            vx = random.uniform(-1, 1) + mouse_vel[0] * 0.2
            vy = random.uniform(-1, 1) + mouse_vel[1] * 0.2
            
            colors = [(150, 200, 255), (200, 220, 255), (255, 255, 255), (180, 220, 255)]
            color = random.choice(colors)
            
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, vx, vy, color, size, "flowing_stream", initial_life=120))

    def create_bouncing_collision(self, x, y):
        for _ in range(5):
            vx = random.uniform(-8, 8)
            vy = random.uniform(-10, -5)
            
            hue = random.random()
            rgb = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            size = random.randint(8, 15)
            self.particles.append(Particle(x, y, vx, vy, color, size, "bouncing_collision"))

    def create_explosion_implosion(self, x, y, is_implosion):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            colors = [(255, 100, 0), (255, 200, 50), (255, 50, 50), (200, 0, 0), (255, 255, 100)]
            color = random.choice(colors)
            
            size = random.randint(4, 8)
            self.particles.append(Particle(x, y, vx, vy, color, size, "explosion_implosion", target_pos=(x,y) if is_implosion else None, initial_life=60))

    def create_wave_ripple(self, x, y):
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            colors = [(50, 150, 255), (100, 200, 255), (150, 220, 255), (200, 240, 255)]
            color = random.choice(colors)
            
            size = random.randint(5, 10)
            self.particles.append(Particle(x, y, vx, vy, color, size, "wave_ripple", initial_life=90))

    def create_path_follower(self, x, y, mouse_vel):
        for _ in range(3):
            vx = random.uniform(-0.5, 0.5) + mouse_vel[0] * 0.5
            vy = random.uniform(-0.5, 0.5) + mouse_vel[1] * 0.5
            
            hue = random.random()
            rgb = colorsys.hsv_to_rgb(hue, 0.5, 0.8)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            size = random.randint(2, 4)
            self.particles.append(Particle(x, y, vx, vy, color, size, "path_follower", initial_life=150))

    def create_spring_attraction(self, x, y):
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Gentle, pastel colors for spring effect
            hue = random.random()
            rgb = colorsys.hsv_to_rgb(hue, 0.6, 0.9)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            size = random.randint(3, 6)
            self.particles.append(Particle(x, y, vx, vy, color, size, "spring_attraction"))

    def create_pixel_painter(self, x, y):
        # Create a single particle that acts as a "pixel"
        color = self.get_next_pixel_color()
        self.particles.append(Particle(x, y, 0, 0, color, special_type="pixel_painter"))

    def create_chain_reaction(self, x, y):
        # Create a single "starter" particle that immediately triggers an explosion
        color = (255, 100, 0) # Fiery color for the explosion
        size = random.randint(5, 8)
        self.particles.append(Particle(x, y, 0, 0, color, size, "chain_starter", initial_life=1)) # Very short life for starter

    def create_light_tracer(self, x, y, mouse_vel):
        # Create a single light tracer particle with velocity influenced by mouse
        vx = random.uniform(-1, 1) + mouse_vel[0] * 0.5
        vy = random.uniform(-1, 1) + mouse_vel[1] * 0.5
        
        # Bright, vibrant colors
        hue = random.random()
        rgb = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        
        self.particles.append(Particle(x, y, vx, vy, color, size=2, special_type="light_tracer"))

    def create_sound_visualizer(self, x, y):
        # Create particles that will pulse
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Bright, varied colors
            hue = random.random()
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            size = random.randint(4, 8)
            self.particles.append(Particle(x, y, vx, vy, color, size, "sound_visualizer"))

    def create_constellation(self, x, y):
        for _ in range(1): # Only 1 per click
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            
            # Subtle, star-like colors (whites, light blues, purples)
            colors = [(255, 255, 255), (200, 220, 255), (180, 200, 255), (220, 200, 255)]
            color = random.choice(colors)
            
            size = random.randint(2, 4)
            self.particles.append(Particle(x, y, vx, vy, color, size, "constellation"))
    
    def update(self, mouse_pos=None, mouse_buttons=None): # Added mouse_buttons parameter
        # Update simulated beat for sound visualizer
        self.simulated_beat_timer += self.simulated_beat_frequency
        self.simulated_beat_strength = (math.sin(self.simulated_beat_timer) + 1) / 2 # 0 to 1 pulse

        # Update particles and collect any new particles generated by them
        new_particles = []
        # Create a copy of the list to iterate over, as particles might be added/removed during the loop
        current_particles = list(self.particles) 
        for particle in current_particles:
            # Pass all_particles for inter-particle forces (e.g., spring_attraction repulsion, constellation connections)
            # Pass simulated_beat_strength for sound visualizer
            result = particle.update(mouse_pos, mouse_buttons, self.particles, self.simulated_beat_strength) 
            if isinstance(result, list): # If particle returned a list of new particles
                new_particles.extend(result)
            
        self.particles.extend(new_particles) # Add new particles to the system
        self.particles = [p for p in self.particles if p.life > 0] # Filter out dead particles
            
        # Limit particle count
        if len(self.particles) > MAX_PARTICLES:
            self.particles = self.particles[-MAX_PARTICLES:] # Keep the newest particles
    
    def draw(self, screen):
        # Draw constellation lines before particles for layering
        if self.mode == "constellation":
            for i, p1 in enumerate(self.particles):
                for j, p2 in enumerate(self.particles):
                    if i < j and p1.special_type == "constellation" and p2.special_type == "constellation":
                        dist = math.hypot(p1.x - p2.x, p1.y - p2.y)
                        if dist < 100: # Connect if within a certain distance
                            line_alpha = int(255 * (1 - dist / 100) * (p1.life / p1.max_life) * (p2.life / p2.max_life))
                            if line_alpha > 0:
                                line_color = (min(255, p1.color[0] + p2.color[0]) // 2,
                                              min(255, p1.color[1] + p2.color[1]) // 2,
                                              min(255, p1.color[2] + p2.color[2]) // 2,
                                              line_alpha)
                                # Pygame draw.line doesn't support alpha, draw on a surface
                                s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                                pygame.draw.line(s, line_color, (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), 1)
                                screen.blit(s, (0, 0))

        for particle in self.particles:
            particle.draw(screen)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Interactive Particle Physics Sandbox")
    clock = pygame.time.Clock()
    
    particle_system = ParticleSystem()
    running = True
    mouse_pressed = False
    prev_mouse_pos = (0, 0)
    mouse_velocity = (0, 0)
    show_menu = True # New state variable for menu visibility
    
    # Instructions
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    while running:
        dt = clock.tick(FPS)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    particle_system.mode = "fountain"
                elif event.key == pygame.K_2:
                    particle_system.mode = "fireworks"
                elif event.key == pygame.K_3:
                    particle_system.mode = "paint"
                elif event.key == pygame.K_4:
                    particle_system.mode = "electric"
                elif event.key == pygame.K_5:
                    particle_system.mode = "bubbles"
                elif event.key == pygame.K_6:
                    particle_system.mode = "snow"
                elif event.key == pygame.K_7:
                    particle_system.mode = "spiral"
                elif event.key == pygame.K_8:
                    particle_system.mode = "galaxy"
                elif event.key == pygame.K_9:
                    particle_system.mode = "tornado"
                elif event.key == pygame.K_0:
                    particle_system.mode = "rain"
                elif event.key == pygame.K_q:
                    particle_system.mode = "smoke"
                elif event.key == pygame.K_w:
                    particle_system.mode = "confetti"
                elif event.key == pygame.K_e:
                    particle_system.mode = "attractor"
                elif event.key == pygame.K_a:
                    particle_system.mode = "blackhole"
                elif event.key == pygame.K_s:
                    particle_system.mode = "fluid"
                elif event.key == pygame.K_d:
                    particle_system.mode = "crystal"
                elif event.key == pygame.K_f:
                    particle_system.mode = "lightning"
                elif event.key == pygame.K_g:
                    particle_system.mode = "lava"
                elif event.key == pygame.K_h: # Toggle menu visibility
                    show_menu = not show_menu
                elif event.key == pygame.K_j:
                    particle_system.mode = "nebula"
                elif event.key == pygame.K_k:
                    particle_system.mode = "solar"
                elif event.key == pygame.K_l:
                    particle_system.mode = "vortex"
                elif event.key == pygame.K_m:
                    particle_system.mode = "constellation"
                elif event.key == pygame.K_n:
                    particle_system.mode = "sound_visualizer"
                elif event.key == pygame.K_o:
                    particle_system.mode = "swarm"
                elif event.key == pygame.K_p:
                    particle_system.mode = "gravity_field"
                elif event.key == pygame.K_r:
                    particle_system.mode = "flowing_stream"
                elif event.key == pygame.K_t:
                    particle_system.mode = "bouncing_collision"
                elif event.key == pygame.K_y:
                    particle_system.mode = "explosion_implosion"
                elif event.key == pygame.K_u:
                    particle_system.mode = "wave_ripple"
                elif event.key == pygame.K_i:
                    particle_system.mode = "path_follower"
                elif event.key == pygame.K_z:
                    particle_system.mode = "spring_attraction"
                elif event.key == pygame.K_x:
                    particle_system.mode = "pixel_painter"
                elif event.key == pygame.K_c:
                    particle_system.mode = "chain_reaction"
                elif event.key == pygame.K_b:
                    particle_system.mode = "light_tracer"
                elif event.key == pygame.K_LEFTBRACKET: # Corrected: Aurora
                    particle_system.mode = "aurora"
                elif event.key == pygame.K_RIGHTBRACKET: # Corrected: Geyser
                    particle_system.mode = "geyser"
                elif event.key == pygame.K_v: # Clear particles
                    particle_system.particles.clear()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pressed = False
                
        # Mouse interaction
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed() # Get state of all mouse buttons (left, middle, right)
        mouse_velocity = (mouse_pos[0] - prev_mouse_pos[0], 
                         mouse_pos[1] - prev_mouse_pos[1])
        prev_mouse_pos = mouse_pos
        
        if mouse_pressed:
            if particle_system.mode == "fountain":
                particle_system.create_fountain(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "fireworks":
                if random.random() < 0.1:
                    particle_system.create_firework(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "paint":
                particle_system.create_paint_splash(mouse_pos[0], mouse_pos[1], mouse_velocity)
            elif particle_system.mode == "electric":
                particle_system.create_electric_storm(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "bubbles":
                particle_system.create_bubbles(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "snow":
                particle_system.create_snow(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "spiral":
                particle_system.create_spiral(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "galaxy":
                if random.random() < 0.3:
                    particle_system.create_galaxy(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "tornado":
                particle_system.create_tornado(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "rain":
                particle_system.create_rain(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "smoke":
                particle_system.create_smoke(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "confetti":
                particle_system.create_confetti(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "attractor":
                particle_system.create_attractor(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "blackhole":
                particle_system.create_blackhole(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "fluid":
                particle_system.create_fluid(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "crystal":
                particle_system.create_crystal(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "lightning":
                if random.random() < 0.2:
                    particle_system.create_lightning(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "lava":
                particle_system.create_lava(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "firefly":
                if random.random() < 0.1:
                    particle_system.create_firefly(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "nebula":
                if random.random() < 0.05:
                    particle_system.create_nebula(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "solar":
                particle_system.create_solar(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "vortex":
                particle_system.create_vortex(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "aurora":
                if random.random() < 0.05:
                    particle_system.create_aurora(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "geyser":
                particle_system.create_geyser(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "swarm":
                particle_system.create_swarm(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "gravity_field":
                particle_system.create_gravity_field(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "flowing_stream":
                particle_system.create_flowing_stream(mouse_pos[0], mouse_pos[1], mouse_velocity)
            elif particle_system.mode == "bouncing_collision":
                particle_system.create_bouncing_collision(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "explosion_implosion":
                if mouse_buttons[0]: # Left click for explosion
                    particle_system.create_explosion_implosion(mouse_pos[0], mouse_pos[1], False)
                elif mouse_buttons[2]: # Right click for implosion
                    particle_system.create_explosion_implosion(mouse_pos[0], mouse_pos[1], True)
            elif particle_system.mode == "wave_ripple":
                particle_system.create_wave_ripple(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "path_follower":
                particle_system.create_path_follower(mouse_pos[0], mouse_pos[1], mouse_velocity)
            elif particle_system.mode == "spring_attraction":
                particle_system.create_spring_attraction(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "pixel_painter":
                particle_system.create_pixel_painter(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "chain_reaction":
                particle_system.create_chain_reaction(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "light_tracer": # New mode
                particle_system.create_light_tracer(mouse_pos[0], mouse_pos[1], mouse_velocity)
            elif particle_system.mode == "sound_visualizer": # New mode
                particle_system.create_sound_visualizer(mouse_pos[0], mouse_pos[1])
            elif particle_system.mode == "constellation": # New mode
                particle_system.create_constellation(mouse_pos[0], mouse_pos[1])

        # Update
        particle_system.update(mouse_pos, mouse_buttons) 
        
        # Draw
        screen.fill(BLACK)
        particle_system.draw(screen)
        
        # Draw UI (only if show_menu is True)
        if show_menu:
            title = font.render("Interactive Particle Physics Sandbox", True, WHITE)
            screen.blit(title, (10, 10))
            
            mode_text = small_font.render(f"Mode: {particle_system.mode.title()}", True, WHITE)
            screen.blit(mode_text, (10, 50))
            
            instructions = [
                "Hold mouse to create particles",
                "1: Fountain  2: Fireworks  3: Paint",
                "4: Electric  5: Bubbles    6: Snow", 
                "7: Spiral    8: Galaxy     9: Tornado",
                "0: Rain      Q: Smoke      W: Confetti", 
                "E: Attractor A: Blackhole  S: Fluid",
                "D: Crystal   F: Lightning  G: Lava",
                "H: Toggle Menu J: Nebula     K: Solar",
                "L: Vortex    M: Constellation N: Sound Visualizer",
                "O: Swarm     P: Gravity Field (Right-click to repel)",
                "R: Flowing Stream T: Bouncing Collision",
                "Y: Explosion/Implosion (Right-click for Implosion)",
                "U: Wave/Ripple I: Path Follower",
                "Z: Spring Attraction X: Pixel Painter C: Chain Reaction",
                "B: Light Tracer [: Aurora    ]: Geyser", # Instructions
                "V: Clear particles"
            ]
            
            # Adjust instruction display to fit more lines
            for i, instruction in enumerate(instructions):
                text = small_font.render(instruction, True, WHITE)
                screen.blit(text, (10, 80 + i * 25))
            
            particle_count = small_font.render(f"Particles: {len(particle_system.particles)}", True, WHITE)
            screen.blit(particle_count, (WIDTH - 150, 10))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()

