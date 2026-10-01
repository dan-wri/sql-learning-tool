import { useEffect, useRef } from 'react'
import { EditorView, basicSetup } from 'codemirror'
import { Compartment } from '@codemirror/state'
import { sql, SQLite } from '@codemirror/lang-sql'

function sqlLanguage(schema) {
  return sql({ dialect: SQLite, schema, upperCaseKeywords: true })
}

// Uncontrolled: initialValue is only read on mount; changes are reported through onChange.
export default function SqlEditor({ initialValue = '', onChange, schema = {} }) {
  const hostRef = useRef(null)
  const viewRef = useRef(null)
  const languageRef = useRef(new Compartment())
  const onChangeRef = useRef(onChange)

  useEffect(() => {
    onChangeRef.current = onChange
  }, [onChange])

  useEffect(() => {
    const view = new EditorView({
      parent: hostRef.current,
      doc: initialValue,
      extensions: [
        basicSetup,
        languageRef.current.of(sqlLanguage({})),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            onChangeRef.current?.(update.state.doc.toString())
          }
        }),
      ],
    })
    viewRef.current = view
    return () => view.destroy()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    viewRef.current?.dispatch({
      effects: languageRef.current.reconfigure(sqlLanguage(schema)),
    })
  }, [schema])

  return <div className="sql-editor" ref={hostRef} data-testid="sql-editor" />
}
