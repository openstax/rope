import { useState } from 'react'

export function Counter(): JSX.Element {
  const [count, setCount] = useState(0)
  return (
    <button type="button" onClick={() => { setCount((count) => count + 1) }}>
      Counter {count}
    </button>
  )
}
