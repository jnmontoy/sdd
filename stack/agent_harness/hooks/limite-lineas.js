#!/usr/bin/env node
/**
 * Hook PostToolUse (Write|Edit): tras escribir un archivo, cuenta sus líneas y avisa si pasa el aviso o el límite de
 * su tipo según SDD BP-23 (.tsx/.ts 300/500, .css 500/800, .py 400/600). No bloquea: le deja el aviso al asistente
 * (para que divida antes de seguir agregando) y al usuario. Los archivos generados, migraciones y JSON no cuentan.
 */
const fs = require('fs')
const path = require('path')

const LIMITES = {
  '.tsx': { aviso: 300, limite: 500 },
  '.ts': { aviso: 300, limite: 500 },
  '.css': { aviso: 500, limite: 800 },
  '.py': { aviso: 400, limite: 600 },
}

// Excepciones de BP-23: generados, migraciones, dependencias y salidas de build
const IGNORAR = [
  /(^|[\\/])(node_modules|venv|\.venv|dist|build|coverage|android|ios|\.expo)[\\/]/i,
  /(^|[\\/])migrations[\\/]/i,
  /\.generated\.ts$/i,
  /\.d\.ts$/i,
  /\.min\.(js|css)$/i,
]

const contarLineas = (texto) => {
  if (!texto) return 0
  const total = texto.split('\n').length
  return texto.endsWith('\n') ? total - 1 : total
}

let entrada = ''
process.stdin.on('data', (d) => (entrada += d))
process.stdin.on('end', () => {
  try {
    const datos = entrada ? JSON.parse(entrada) : {}
    const archivo = (datos.tool_input && datos.tool_input.file_path) || ''
    const tope = LIMITES[path.extname(archivo).toLowerCase()]
    if (!archivo || !tope || IGNORAR.some((r) => r.test(archivo)) || !fs.existsSync(archivo)) return

    const lineas = contarLineas(fs.readFileSync(archivo, 'utf8'))
    if (lineas <= tope.aviso) return

    const nombre = path.basename(archivo)
    const pasado = lineas > tope.limite
    const mensaje = pasado
      ? `${nombre}: ${lineas} líneas, supera el límite de ${tope.limite} (SDD BP-23). Antes de agregarle más código, ` +
        'desacóplalo (componentes, hooks o estilos por componente en el frontend; funciones o módulos por dominio en ' +
        'el backend) sin cambiar el comportamiento, o explica por qué no aplica.'
      : `${nombre}: ${lineas} líneas, pasó el aviso de ${tope.aviso} (límite ${tope.limite}, SDD BP-23). ` +
        'Conviene planear la división.'
    console.log(
      JSON.stringify({
        systemMessage: mensaje,
        hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: mensaje },
      })
    )
  } catch {
    // Si algo falla, no interrumpir el trabajo
  }
})
