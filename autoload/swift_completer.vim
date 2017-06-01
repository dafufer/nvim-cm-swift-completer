let s:placeholder_pattern = '\&<#\%(T##\)\?\%([^#]\+##\)\?\([^#]\+\)#>'

function! swift_completer#jump_to_placeholder()
  if &filetype !=# 'swift'
    return ''
  end

  if !search(s:placeholder_pattern)
    return ''
  endif

  return "\<ESC>:call swift_completer#begin_replacing_placeholder()\<CR>"
endfunction

function! swift_completer#begin_replacing_placeholder()
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
