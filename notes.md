1. Preheat the oven to 350 degrees F (175 degrees C).
--> preheat oven

2. Combine sugar, flour, and salt in a saucepan. Gradually stir in milk. Cook, stirring constantly, over medium heat until mixture boils and thickens. Continue to cook and stir for 2 more minutes, then remove from the heat.
--> boiled sugar,flour, salk, milk mixture

3. Place egg yolks in a medium bowl; whisk in a small amount of the hot milk mixture until smooth, then gradually whisk egg yolk mixture into the saucepan. Cook over medium-low heat, stirring constantly until mixture coats the back of a spoon, about 2 more minutes. Remove from heat and stir in butter and vanilla.

4. Fill pastry shell with sliced bananas; pour pudding mixture on top to cover.
-> pudding mixture

5. Bake in the preheated oven until filling sets, 12 to 15 minutes. Let pie cool completely on a wire rack, then chill pie in the refrigerator for at least 1 hour before serving.

-------------

- scenarios:
 when user ask about ingredients on this step but there are no ingredients methoed there. 



res:  Preheat the oven to 350 degrees F (175 degrees C). ('350', 'F') [] None ['preheat'] ['oven']
res:  Combine sugar, flour, and salt in a saucepan. ('medium', 'heat') ['salt'] None ['combine'] ['pan', 'saucepan']
res:  Gradually stir in milk. ('medium', 'heat') ['salt'] None ['stir'] ['pan', 'saucepan']
res:  Cook, stirring constantly, over medium heat until mixture boils and thickens. ('medium', 'heat') ['salt'] None ['heat', 'boil', 'stir'] ['pan', 'saucepan']
res:  Continue to cook and stir for 2 more minutes, then remove from the heat. ('medium', 'heat') ['salt'] ('2', '2', 'minutes') ['cook', 'heat', 'stir', 'remove'] ['pan', 'saucepan']
res:  Place egg yolks in a medium bowl. None ['egg yolks', 'butter', 'milk'] None ['place'] []
res:  whisk in a small amount of the hot milk mixture until smooth, then gradually whisk egg yolk mixture into the saucepan. None ['egg yolks', 'butter', 'milk'] None ['yolk', 'whisk'] ['pan', 'whisk', 'saucepan']     
res:  Cook over medium-low heat, stirring constantly until mixture coats the back of a spoon, about 2 more minutes. None ['egg yolks', 'butter', 'milk'] ('2', '2', 'minutes') ['cook', 'heat', 'coat', 'stir'] ['pan', 'whisk', 'saucepan']
res:  Remove from heat and stir in butter and vanilla. None ['egg yolks', 'butter', 'milk'] None ['heat', 'remove', 'stir'] ['pan', 'whisk', 'saucepan']
res:  Fill pastry shell with sliced bananas. None ['baked pastry shell', 'bananas'] None ['fill'] []
res:  pour pudding mixture on top to cover. None ['baked pastry shell', 'bananas'] None ['pour', 'cover'] [] 
res:  Bake in the preheated oven until filling sets, 12 to 15 minutes. None [] ('12', '15', 'minutes') ['bake', 'fill'] ['oven']
res:  Let pie cool completely on a wire rack, then chill pie in the refrigerator for at least 1 hour before serving. None [] ('1', '1', 'hour') ['serve', 'cool', 'chill'] ['refrigerator']