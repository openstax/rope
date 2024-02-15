// https://vike.dev/useData

import { usePageContext } from '../components/usePageContext'

/** https://vike.dev/useData */
export function useData<Data>(): Data {
  const { data } = usePageContext()
  return data as Data
}
