import { useEffect, useState } from 'react'
import { pingHealth } from '../utils/api'

export function useApiHealth(intervalMs = 15000) {
  const [online, setOnline] = useState(true)

  useEffect(() => {
    let cancelled = false
    const check = async () => {
      const ok = await pingHealth()
      if (!cancelled) setOnline(ok)
    }
    check()
    const id = setInterval(check, intervalMs)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [intervalMs])

  return online
}
