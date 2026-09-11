@csrf_exempt
def get_love(request):
    # Разрешаем только POST
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)
    # Пытаемся распарсить JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    # Проверка на секретный код доступа
    if data.get('code') != "sk*Fu+qm4Cka0P1":
        return JsonResponse({'error': 'Access denied'}, status=403)

    author_id = int(data.get('author_id'))
    nickname = data.get('nickname', '')
    response = ''

    obj, created = Love.objects.get_or_create(
        author_id=author_id,
    )
    obj.author_name = nickname

    # проверяем дату последнего успешного выполнения команды !love, если дата не совпадает с датой вызова, тогда
    # выполняем обновляем дату выполнения команды
    if created or obj.updated_at.date() != timezone.now().date():
        love_variants = TextSample.objects.filter(pk=11).first()
        if love_variants:
            love_variants = love_variants.text.split("\r\n")
            random_integer = random.randint(0, 100)
            response = f'Сегодня любишь yrarami на {random_integer}%\n'
            if random_integer == 0:
                response += love_variants[1]
            elif 1 <= random_integer <= 20:
                response += love_variants[3]
            elif 21 <= random_integer <= 40:
                response += love_variants[5]
            elif 41 <= random_integer <= 60:
                response += love_variants[7]
            elif 61 <= random_integer <= 80:
                response += love_variants[9]
            elif 81 <= random_integer <= 99:
                response += love_variants[11]
            elif random_integer == 100:
                response += love_variants[13]
            obj.counter = 1 if created else obj.counter + 1
        else:
            response = "Ой, что-то пошло не так 😔"
    else:
        response = "Вы уже спрашивали сегодня, лимит на любовь исчерпан, приходите завтра 😉"

    obj.save()

    return JsonResponse({"response": response})
