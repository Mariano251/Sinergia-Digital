const {
  calcularScoring,
  CART_VALUE_MAX,
  U_ALTA,
  U_MEDIA,
  AB_CASTIGO,
} = require('./scoringService');

const sesionesTanda3 = require('./sesiones-tanda3.json');

describe('calcularScoring — constantes del algoritmo vigente', () => {
  test('los umbrales son los del nodo de n8n que corrio la Tanda 3', () => {
    expect(CART_VALUE_MAX).toBe(200000);
    expect(U_ALTA).toBe(70);
    expect(U_MEDIA).toBe(30);
    expect(AB_CASTIGO).toBe(4);
  });
});

describe('calcularScoring — puntuacion por valor de carrito', () => {
  // puntuacion = 100 x min(cart_value / 200000, 1), redondeada a dos decimales
  test.each([
    { cart_value: 0, esperado: 0 },
    { cart_value: 24000, esperado: 12 },
    { cart_value: 59000, esperado: 29.5 },
    { cart_value: 60000, esperado: 30 },
    { cart_value: 140000, esperado: 70 },
    { cart_value: 200000, esperado: 100 },
  ])('$cart_value -> $esperado puntos', ({ cart_value, esperado }) => {
    expect(calcularScoring({ cart_value, previous_abandonment_count: 0 }).puntuacion).toBe(esperado);
  });

  test('un carrito por encima del maximo se capea en 100 y no sigue creciendo', () => {
    expect(calcularScoring({ cart_value: 1000000, previous_abandonment_count: 0 }).puntuacion).toBe(100);
  });

  test('la puntuacion se redondea a dos decimales', () => {
    expect(calcularScoring({ cart_value: 105000, previous_abandonment_count: 0 }).puntuacion).toBe(52.5);
    expect(calcularScoring({ cart_value: 69000, previous_abandonment_count: 0 }).puntuacion).toBe(34.5);
  });

  test('acepta el valor como texto, igual que cuando llega del payload', () => {
    expect(calcularScoring({ cart_value: '160000', previous_abandonment_count: '0' }).puntuacion).toBe(80);
  });

  test('un valor ausente o no numerico cuenta como 0', () => {
    expect(calcularScoring({}).puntuacion).toBe(0);
    expect(calcularScoring({ cart_value: 'no-es-un-numero' }).puntuacion).toBe(0);
  });

  test('sin argumentos no rompe: devuelve BAJA con 0 puntos', () => {
    expect(calcularScoring()).toEqual({ puntuacion: 0, prioridad: 'BAJA', degradado: false });
  });
});

describe('calcularScoring — clasificacion por tramos', () => {
  test.each([
    { cart_value: 200000, esperado: 'ALTA' },
    { cart_value: 140000, esperado: 'ALTA' },   // justo en el umbral de ALTA
    { cart_value: 139000, esperado: 'MEDIA' },  // un paso por debajo
    { cart_value: 60000, esperado: 'MEDIA' },   // justo en el umbral de MEDIA
    { cart_value: 59000, esperado: 'BAJA' },    // un paso por debajo
    { cart_value: 0, esperado: 'BAJA' },
  ])('$cart_value sin abandonos -> $esperado', ({ cart_value, esperado }) => {
    expect(calcularScoring({ cart_value, previous_abandonment_count: 0 }).prioridad).toBe(esperado);
  });
});

describe('calcularScoring — castigo por abandono recurrente', () => {
  test('con menos de 4 abandonos no se degrada', () => {
    for (const ab of [0, 1, 2, 3]) {
      const r = calcularScoring({ cart_value: 200000, previous_abandonment_count: ab });
      expect(r.prioridad).toBe('ALTA');
      expect(r.degradado).toBe(false);
    }
  });

  test('a partir de 4 abandonos baja exactamente un nivel', () => {
    expect(calcularScoring({ cart_value: 200000, previous_abandonment_count: 4 }).prioridad).toBe('MEDIA');
    expect(calcularScoring({ cart_value: 100000, previous_abandonment_count: 4 }).prioridad).toBe('BAJA');
  });

  test('BAJA no puede degradarse por debajo de BAJA', () => {
    expect(calcularScoring({ cart_value: 40000, previous_abandonment_count: 9 }).prioridad).toBe('BAJA');
  });

  test('el castigo no cambia la puntuacion, solo el nivel', () => {
    const sinCastigo = calcularScoring({ cart_value: 200000, previous_abandonment_count: 3 });
    const conCastigo = calcularScoring({ cart_value: 200000, previous_abandonment_count: 4 });
    expect(conCastigo.puntuacion).toBe(sinCastigo.puntuacion);
    expect(conCastigo.prioridad).not.toBe(sinCastigo.prioridad);
  });

  test('mas alla del umbral el castigo no se acumula: sigue siendo un solo nivel', () => {
    const cuatro = calcularScoring({ cart_value: 200000, previous_abandonment_count: 4 });
    const cien = calcularScoring({ cart_value: 200000, previous_abandonment_count: 100 });
    expect(cien).toEqual(cuatro);
  });

  test('marca en degradado si aplico el castigo', () => {
    expect(calcularScoring({ cart_value: 200000, previous_abandonment_count: 4 }).degradado).toBe(true);
  });

  test('un contador ausente o no numerico cuenta como 0', () => {
    expect(calcularScoring({ cart_value: 200000 }).prioridad).toBe('ALTA');
    expect(calcularScoring({ cart_value: 200000, previous_abandonment_count: null }).degradado).toBe(false);
  });
});

describe('calcularScoring — cart_stage NO participa del calculo', () => {
  const etapas = ['browsing', 'cart', 'checkout_started', 'payment_page', 'etapa_inexistente', undefined];

  test('las cuatro etapas y una desconocida dan el mismo resultado', () => {
    const referencia = calcularScoring({ cart_value: 120000, previous_abandonment_count: 1, cart_stage: 'cart' });
    for (const cart_stage of etapas) {
      expect(calcularScoring({ cart_value: 120000, previous_abandonment_count: 1, cart_stage })).toEqual(referencia);
    }
  });
});

describe('calcularScoring — reproduce las 55 sesiones reales de la Tanda 3', () => {
  // Fixture: sesiones-tanda3.json, extraido de validacion/datos-crudos-tanda3-55-sesiones.csv,
  // que a su vez sale de execution_data de n8n (ejecuciones 158 a 212 del 11/09/2026).
  test('el fixture tiene las 55 sesiones', () => {
    expect(sesionesTanda3).toHaveLength(55);
  });

  test.each(sesionesTanda3)(
    'N $n ($escenario): $$$cart_value, $previous_abandonment_count abandonos -> $prioridad',
    ({ cart_value, cart_stage, previous_abandonment_count, puntuacion, prioridad }) => {
      const r = calcularScoring({ cart_value, cart_stage, previous_abandonment_count });
      expect(r.puntuacion).toBe(puntuacion);
      expect(r.prioridad).toBe(prioridad);
    }
  );

  test('el reparto global coincide con el de la corrida: ALTA 11, MEDIA 26, BAJA 18', () => {
    const reparto = { ALTA: 0, MEDIA: 0, BAJA: 0 };
    for (const s of sesionesTanda3) {
      reparto[calcularScoring(s).prioridad] += 1;
    }
    expect(reparto).toEqual({ ALTA: 11, MEDIA: 26, BAJA: 18 });
  });

  test('las 15 sesiones con 4 o mas abandonos quedan marcadas como degradadas', () => {
    const degradadas = sesionesTanda3.filter((s) => calcularScoring(s).degradado);
    expect(degradadas).toHaveLength(15);
    expect(degradadas.every((s) => s.previous_abandonment_count >= AB_CASTIGO)).toBe(true);
  });
});
