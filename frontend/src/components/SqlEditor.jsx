import { useEffect, useRef } from 'react'
import { EditorView, basicSetup } from 'codemirror'
import { keymap } from '@codemirror/view'
import { Compartment, Prec } from '@codemirror/state'
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language'
import { tags } from '@lezer/highlight'
import { sql, SQLite } from '@codemirror/lang-sql'

function sqlLanguage(schema) {
  return sql({ dialect: SQLite, schema, upperCaseKeywords: true })
}

const studioTheme = EditorView.theme(
  {
    '&': { backgroundColor: 'var(--surface-subtle)', color: 'var(--text)', fontSize: '14px' },
    '&.cm-focused': { outline: 'none' },
    '.cm-scroller': { fontFamily: 'var(--font-mono)', lineHeight: '1.65', overflow: 'auto' },
    '.cm-content': { padding: '12px 0', caretColor: 'var(--primary)' },
    '.cm-line': { padding: '0 16px 0 8px' },
    '.cm-gutters': {
      backgroundColor: 'var(--surface-hover)',
      color: 'var(--text-muted)',
      border: 'none',
      borderRight: '1px solid var(--border)',
    },
    '.cm-activeLine': { backgroundColor: 'color-mix(in srgb, var(--primary) 5%, transparent)' },
    '.cm-activeLineGutter': { backgroundColor: 'var(--primary-soft)', color: 'var(--primary)' },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, ::selection': {
      backgroundColor: 'color-mix(in srgb, var(--primary) 22%, transparent)',
    },
    '.cm-cursor': { borderLeftColor: 'var(--primary)' },
    '.cm-tooltip': {
      border: '1px solid var(--border)',
      borderRadius: '8px',
      boxShadow: 'var(--shadow-pop)',
      backgroundColor: 'var(--surface)',
      overflow: 'hidden',
    },
    '.cm-tooltip-autocomplete ul li[aria-selected]': { backgroundColor: 'var(--primary-soft)', color: 'var(--text)' },
  },
  { dark: false },
)

const studioHighlight = HighlightStyle.define([
  { tag: tags.keyword, color: '#4338ca', fontWeight: '600' },
  { tag: [tags.string, tags.special(tags.string)], color: '#0f766e' },
  { tag: [tags.number, tags.bool, tags.null], color: '#b45309' },
  { tag: [tags.comment, tags.lineComment, tags.blockComment], color: '#64748b', fontStyle: 'italic' },
  { tag: [tags.operator, tags.punctuation], color: '#475569' },
  { tag: [tags.typeName, tags.standard(tags.name)], color: '#7c3aed' },
])

// Uncontrolled: initialValue is only read on mount; changes are reported through onChange.
export default function SqlEditor({ initialValue = '', onChange, onSubmit, schema = {} }) {
  const hostRef = useRef(null)
  const viewRef = useRef(null)
  const languageRef = useRef(new Compartment())
  const onChangeRef = useRef(onChange)
  const onSubmitRef = useRef(onSubmit)

  useEffect(() => {
    onChangeRef.current = onChange
    onSubmitRef.current = onSubmit
  }, [onChange, onSubmit])

  useEffect(() => {
    const view = new EditorView({
      parent: hostRef.current,
      doc: initialValue,
      extensions: [
        basicSetup,
        languageRef.current.of(sqlLanguage({})),
        studioTheme,
        syntaxHighlighting(studioHighlight),
        Prec.highest(
          keymap.of([
            {
              key: 'Mod-Enter',
              run: () => {
                onSubmitRef.current?.()
                return true
              },
            },
          ]),
        ),
        EditorView.contentAttributes.of({ 'aria-label': 'SQL editor' }),
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
