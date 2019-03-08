ActiveSupport.on_load(:after_initialize) do
  ApplicationController.send :rescue_from, FoodsoftVokomokum::VokomokumException, &proc {|exception|
    flash[:error] = t('errors.general_msg', msg: exception.message)
  }
end
