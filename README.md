# Вертолеты не отбрасывают тень
А я отбрасываю.

Материалы к посту про Ingenuity. 

Столб с указателями:
* ./**videos** - Разные видео из статьи и картинки со спектрами для них. Внутри есть папка ./frames, но фреймы весили неприлично много, поэтому там однострочник для их извлечения (нужен ffmpeg)
* ./**raw_images** - некоторые сырые картинки, если вам очень надо что-то поизмерять.

* ./**pls_compare** - картинки из той части, где я сравниваю симулятор плохого затвора с реальностью

* ./**trash_can** - Мусорка со смятой бумагой и картинками. То, что было выпилено из текста или недоделано.

* ./**shadow_anim** - Анимации разных параметров затвора
 
* ./**scripts** - Говнокод из статьи. А именно:

 **doppler_graph** - Рисовалка графика скорости по Доплеровскому сдвигу
 
**doppler_sim** - Симулятор жужжащего вертолета (его можно научить писать в wav файлы, если запихать туда chirp.py)

**falloff** - Комплекс программного обеспечения для фотограмметрии

**pls_simulation** - Симулятор неэффективного глобального затвора
