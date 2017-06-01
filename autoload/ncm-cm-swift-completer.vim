" Use the toolchain specified with `com.apple.dt.toolchain.{name}`.
"function! ncm-cm-swift-completer#use_toolchain(name)
    "call ncm-cm-swift-completer#use_custom_toolchain(s:get_xcode_toolchain(a:name))
"endfunction

" Use the custom toolchain specified with the given identifier.
"function! ncm-cm-swift-completer#use_custom_toolchain(identifier)
    "let g:ncm-cm-swift-completer#toolchain = a:identifier
"endfunction

"func s:get_xcode_toolchain(name)
    "return 'com.apple.dt.toolchain.' . a:name
"endfunction



let s:placeholder_pattern = '<#\%(T##\)\?\%([^#]\+##\)\?\([^#]\+\)#>'

function! s:jump_to_placeholder()
  if &filetype !=# 'swift'
    return ''
  end

  if !search(s:placeholder_pattern)
    return ''
  endif

  return "\<ESC>:call ncm-cm-swift-completer#begin_replacing_placeholder()\<CR>"
endfunction

function! ncm-cm-swift-completer#begin_replacing_placeholder()
    if mode() !=# 'n'
        return
    endif

    let l:pattern = s:placeholder_pattern

    let [l:line, l:column] = searchpos(l:pattern)
    if l:line == 0 && l:column == 0
        return
    end

    execute printf(':%d s/%s//', l:line, l:pattern)

    call cursor(l:line, l:column)

    startinsert
endfunction
